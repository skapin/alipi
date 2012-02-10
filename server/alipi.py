from flask import Flask
from flask import request
from flask import render_template
import lxml.html
import cgi
import pymongo
from bson import Code
import urllib2
import StringIO
import gdata.gauth
import gdata.blogger.client
from flask import g
from flask import redirect
from urllib import quote_plus
from urllib import unquote_plus
app = Flask(__name__)
connection = pymongo.Connection('localhost',27017) #Create the object once and use it.
db = connection['dev_alipi']
collection = db['post']
@app.route('/')
def start_page() :
    d = {}
    d['foruri'] = request.args['foruri']
    myhandler1 = urllib2.Request(d['foruri'],headers={'User-Agent':"Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11"}) #A fix to send user-agents, so that sites render properly.
    try:
        a = urllib2.urlopen(myhandler1)
        if a.geturl() != d['foruri']:
            return "There was a server redirect, please click on the <a href='http://dev.a11y.in/web?foruri={0}'>link</a> to continue.".format(quote_plus(a.geturl()))
        else:
            page = a.read()
            a.close()
    except ValueError:
        return "The link is malformed, click <a href='http://dev.a11y.in/web?foruri={0}&lang={1}&interactive=1'>here</a> to be redirected.".format(quote_plus(unquote_plus(d['foruri'])),request.args['lang'])
    except urllib2.URLError:
        return render_template('error.html')
    try:
        page = unicode(page,'utf-8')  #Hack to fix improperly displayed chars on wikipedia.
    except UnicodeDecodeError:
        pass #Some pages may not need be utf-8'ed
    root = lxml.html.parse(StringIO.StringIO(page)).getroot()
    if request.args.has_key('lang') == False and request.args.has_key('blog') == False:
        root.make_links_absolute(d['foruri'], resolve_base_href = True)
        
        script_test = root.makeelement('script')
        script_edit = root.makeelement('script')
        root.body.append(script_test)
        root.body.append(script_edit)
        script_test.set("src", "http://dev.a11y.in/alipi/ui.js")
        script_test.set("type", "text/javascript")
        script_edit.set("src", "http://dev.a11y.in/alipi/wsgi/page_edit.js")
        script_edit.set("type","text/javascript")
        
        script_jq_mini = root.makeelement('script')
        root.body.append(script_jq_mini)
        script_jq_mini.set("src", "http://code.jquery.com/jquery-1.7.min.js")
        script_jq_mini.set("type", "text/javascript")
        
        style = root.makeelement('link')
        root.body.append(style)
        style.set("rel","stylesheet")
        style.set("type", "text/css")
        style.set("href", "http://dev.a11y.in/alipi/stylesheet.css")

        # if collection.find_one({"about" : request.args['foruri']}) is not None:
        #     overlay1 = root.makeelement('div')
        #     root.body.append(overlay1)
        #     overlay1.set("id", "overlay1")

        #     opt = root.makeelement('option')
        #     opt.text = "Choose a narration"

        script_jq_cust = root.makeelement('script')
        root.body.append(script_jq_cust)
        script_jq_cust.set("src", "https://ajax.googleapis.com/ajax/libs/jqueryui/1.8.16/jquery-ui.min.js")
        script_jq_cust.set("type", "text/javascript")

        style_cust = root.makeelement('link')
        style_cust.set("rel","stylesheet")
        style_cust.set("type", "text/css")
        style_cust.set("href", "http://ajax.googleapis.com/ajax/libs/jqueryui/1.8/themes/ui-lightness/jquery-ui.css")
        root.body.append(style_cust)

        root.body.set("onload","a11ypi.loadOverlay();")
        return lxml.html.tostring(root)

    elif request.args.has_key('lang') == True and request.args.has_key('interactive') == True and request.args.has_key('blog') == False:
        root.make_links_absolute(d['foruri'], resolve_base_href = True)
        script_test = root.makeelement('script')
        script_edit = root.makeelement('script')
        root.body.append(script_test)
        root.body.append(script_edit)
        
        script_jq_mini = root.makeelement('script')
        root.body.append(script_jq_mini)
        script_jq_mini.set("src", "http://ajax.googleapis.com/ajax/libs/jquery/1.7/jquery.min.js")
        script_jq_mini.set("type", "text/javascript")

        script_test.set("src", "http://dev.a11y.in/alipi/ui.js")
        script_test.set("type", "text/javascript")
        script_edit.set("src", "http://dev.a11y.in/alipi/wsgi/page_edit.js")
        script_edit.set("type","text/javascript")
        script_jqui = root.makeelement('script')
        script_jqui.set("type","text/javascript")
        script_jqui.set("src","https://ajax.googleapis.com/ajax/libs/jqueryui/1.8.16/jquery-ui.min.js")
        root.body.append(script_jqui)

        
        ui_css = root.makeelement("link")
        ui_css.set("rel", "stylesheet");
        ui_css.set("type", "text/css");
        ui_css.set("href", "http://ajax.googleapis.com/ajax/libs/jqueryui/1.8/themes/ui-lightness/jquery-ui.css");
        root.body.append(ui_css);
        
        ren_overlay = root.makeelement('div')
        root.body.append(ren_overlay)
        ren_overlay.set("id", "social_overlay")
        
        see_orig = root.makeelement('input')
        ren_overlay.append(see_orig)
        see_orig.set("id", "see_orig-button")
        see_orig.set("type", "submit")
        see_orig.set("onClick", "a11ypi.showOriginal();")
        see_orig.set("value", "See original page")
        see_orig.set("style","position:fixed;left:5px;top:6px;")

        tweet = root.makeelement("a")
        tweet.set("id", "tweet")
        tweet.set("href", "https://twitter.com/share")
        tweet.set("class", "twitter-share-button")
        tweet.set("data-via", "a11ypi")
        tweet.set("data-lang", "en")
        tweet.set("data-url", "http://dev.a11y.in/web?foruri={0}&lang={1}&interactive=1".format(quote_plus(d['foruri']),request.args['lang']))
        tweet.textContent = "Tweet"
        ren_overlay.append(tweet)

        fbroot = root.makeelement("div")
        fbroot.set("id", "fb-root")
        ren_overlay.append(fbroot)

        fblike = root.makeelement("div")
        fblike.set("class", "fb-like")
        fblike.set("data-href", "http://dev.a11y.in/web?foruri={0}&lang={1}&interactive=1".format(quote_plus(d['foruri']),request.args['lang']))
        fblike.set("data-send", "true")
        fblike.set("data-layout", "button_count")
        fblike.set("data-width", "50")
        fblike.set("data-show-faces", "true")
        fblike.set("data-font", "arial")
        ren_overlay.append(fblike)
        
        style = root.makeelement('link')
        root.body.append(style)
        style.set("rel","stylesheet")
        style.set("type", "text/css")
        style.set("href", "http://dev.a11y.in/alipi/stylesheet.css")
        
        # overlay2 = root.makeelement('div')
        # root.body.append(overlay2)
        # overlay2.set("id", "overlay2")
        
        # btn = root.makeelement('input')
        # overlay2.append(btn)
        # btn.set("id", "edit-button")
        # btn.set("type", "submit")
        # btn.set("onClick", "a11ypi.testContext();page_edit('4seiz', '4l85060vb9', '336e2nootv6nxjsvyjov', 'VISUAL', 'false', '');")
        # btn.set("value", "EDIT")
        root.body.set("onload","a11ypi.ren();a11ypi.tweet(); a11ypi.facebook();a11ypi.loadOverlay();")
        return lxml.html.tostring(root)
        
    elif request.args.has_key('lang') == True and request.args.has_key('blog') == False:
        script_jq_mini = root.makeelement('script')
        root.body.append(script_jq_mini)
        script_jq_mini.set("src", "http://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.js")
        script_jq_mini.set("type", "text/javascript")
        d['lang'] = request.args['lang']
        script_test = root.makeelement('script')
        root.body.append(script_test)
        script_test.set("src", "http://dev.a11y.in/alipi/ui.js")
        script_test.set("type", "text/javascript")
        root.body.set("onload","a11ypi.ren()");
        root.make_links_absolute(d['foruri'], resolve_base_href = True)
        return lxml.html.tostring(root)

    elif request.args.has_key('interactive') == True and request.args.has_key('blog') == True and request.args.has_key('lang') == True:
        script_jqui = root.makeelement('script')

        script_test = root.makeelement('script')
        script_test.set("src", "http://dev.a11y.in/alipi/ui.js")
        script_test.set("type", "text/javascript")
        root.body.append(script_test)
        
        script_jq_mini = root.makeelement('script')
        script_jq_mini.set("src", "http://code.jquery.com/jquery-1.7.min.js")
        script_jq_mini.set("type", "text/javascript")
        root.body.append(script_jq_mini)

        script_edit = root.makeelement('script')
        script_edit.set("src", "http://dev.a11y.in/alipi/wsgi/page_edit.js")
        script_edit.set("type","text/javascript")
        root.body.append(script_edit)
        
        script_jqui.set("type","text/javascript")
        script_jqui.set("src","https://ajax.googleapis.com/ajax/libs/jqueryui/1.8.16/jquery-ui.min.js")
        root.body.append(script_jqui)        
        ui_css = root.makeelement("link")
        ui_css.set("rel", "stylesheet");
        ui_css.set("type", "text/css");
        ui_css.set("href", "http://ajax.googleapis.com/ajax/libs/jqueryui/1.8/themes/ui-lightness/jquery-ui.css");
        root.body.append(ui_css);
        
        ren_overlay = root.makeelement('div')
        root.body.append(ren_overlay)
        ren_overlay.set("id", "social_overlay")
        
        see_orig = root.makeelement('input')
        ren_overlay.append(see_orig)
        see_orig.set("id", "see_orig-button")
        see_orig.set("type", "submit")
        see_orig.set("onClick", "a11ypi.showOriginal();")
        see_orig.set("value", "See original page")
        see_orig.set("style","position:fixed;left:5px;top:6px;")

        tweet = root.makeelement("a")
        tweet.set("id", "tweet")
        tweet.set("href", "https://twitter.com/share")
        tweet.set("class", "twitter-share-button")
        tweet.set("data-via", "a11ypi")
        tweet.set("data-lang", "en")
        tweet.set("data-url", "http://dev.a11y.in/web?foruri={0}&lang={1}&interactive=1".format(quote_plus(d['foruri']),request.args['lang']))
        tweet.textContent = "Tweet"
        ren_overlay.append(tweet)

        fbroot = root.makeelement("div")
        fbroot.set("id", "fb-root")
        ren_overlay.append(fbroot)

        fblike = root.makeelement("div")
        fblike.set("class", "fb-like")
        fblike.set("data-href", "http://dev.a11y.in/web?foruri={0}&lang={1}&interactive=1".format(quote_plus(d['foruri']),request.args['lang']))
        fblike.set("data-send", "true")
        fblike.set("data-layout", "button_count")
        fblike.set("data-width", "50")
        fblike.set("data-show-faces", "true")
        fblike.set("data-font", "arial")
        ren_overlay.append(fblike)

        
        style = root.makeelement('link')
        root.body.append(style)
        style.set("rel","stylesheet")
        style.set("type", "text/css")
        style.set("href", "http://dev.a11y.in/alipi/stylesheet.css")
        
        overlay2 = root.makeelement('div')
        root.body.append(overlay2)
        overlay2.set("id", "overlay2")
        
        btn = root.makeelement('input')
        overlay2.append(btn)
        btn.set("id", "edit-button")
        btn.set("type", "submit")
        btn.set("onClick", "a11ypi.testContext();page_edit('4seiz', '4l85060vb9', '336e2nootv6nxjsvyjov', 'VISUAL', 'false', '');")
        btn.set("value", "EDIT")

        script_test = root.makeelement('script')
        root.body.append(script_test)
        script_test.set("src", "http://dev.a11y.in/alipi/ui.js")
        script_test.set("type", "text/javascript")
        root.body.set("onload","a11ypi.filter(); a11ypi.tweet(); a11ypi.facebook();");
        root.make_links_absolute(d['foruri'], resolve_base_href = True)
        return lxml.html.tostring(root)

    elif request.args.has_key('interactive') == False and request.args.has_key('blog') == True:    
        script_test = root.makeelement('script')
        root.body.append(script_test)
        script_test.set("src", "http://dev.a11y.in/alipi/ui.js")
        script_test.set("type", "text/javascript")
        
        script_jq_mini = root.makeelement('script')
        root.body.append(script_jq_mini)
        script_jq_mini.set("src", "http://ajax.googleapis.com/ajax/libs/jquery/1.7/jquery.min.js")
        script_jq_mini.set("type", "text/javascript")

        script_jq_cust = root.makeelement('script')
        root.body.append(script_jq_cust)
        script_jq_cust.set("src", "https://ajax.googleapis.com/ajax/libs/jqueryui/1.8.16/jquery-ui.min.js")
        script_jq_cust.set("type", "text/javascript")

        style_cust = root.makeelement('link')
        style_cust.set("rel","stylesheet")
        style_cust.set("type", "text/css")
        style_cust.set("href", "http://ajax.googleapis.com/ajax/libs/jqueryui/1.8/themes/ui-lightness/jquery-ui.css")
        root.body.append(style_cust)

        style = root.makeelement('link')
        root.body.append(style)
        style.set("rel","stylesheet")
        style.set("type", "text/css")
        style.set("href", "http://dev.a11y.in/alipi/stylesheet.css")

        if collection.find_one({"about" : request.args['foruri']}) is not None:
            overlay1 = root.makeelement('div')
            root.body.append(overlay1)
            overlay1.set("id", "overlay1")

            opt = root.makeelement('option')
            opt.text = "Choose a narration"

            rpl = root.makeelement('select')
            overlay1.append(rpl)
            rpl.append(opt)
            rpl.set("id", "menu-button")
            rpl.set("onclick", "a11ypi.ajax1();")
        root.make_links_absolute(d['foruri'], resolve_base_href = True)
        return lxml.html.tostring(root)

@app.route('/directory')
def show_directory():
    # for i in collection.find():
    #     if i.has_key('about'):
    #         if i['about'] != 'undefined' and i['about'] != '':
    #             ren.append("http://y.a11y.in/web?foruri="+quote_plus(i['about'])+'&lang='+i['lang'])
    query = collection.group(
        key = Code('function(doc){return {"about" : doc.about,"lang":doc.lang}}'),
        condition={"about":{'$regex':'^[/\S/]'}},
        initial={'na': []},
        reduce=Code('function(doc,out){out.na.push(doc.blog)}')
        )
    return render_template('directory.html', name=query, mymodule = quote_plus, myset=set, mylist= list)

@app.route('/getLang')
def get_lang():
    collection = db['alipi_lang']
    term = '^{0}.*'.format(request.args['term'][0])
    query = collection.group(
        key = Code('function(doc){return {"name" : doc.name}}'),
        condition={"name":{'$regex':term, '$options':'i'}},
        initial={'na': []},
        reduce=Code('function(doc,out){out.na.push(doc);}')
        )
    string = {'name':[]}
    if len(query) != 0:
        for i in query:
            for x in i['na']:
                if x != '_id':
                    string['name'].append((x['name']))
    return jsonify(string)

import logging,os
from logging import FileHandler

fil = FileHandler(os.path.join(os.path.dirname(__file__),'logme'),mode='a')
fil.setLevel(logging.ERROR)
app.logger.addHandler(fil)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

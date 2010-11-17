#!/usr/bin/python


import web
import os
import markdown
import commands
import time
from web.contrib.template import render_jinja
import json
import random
import string
from settings import *
#Define URLS
urls = (
	'/sendfile/(.*)','sendfile',
	'/reload/(.*)','reload',
	'/(.*)','home'
)

app = web.application(urls, globals())


#don't touch from here on out
site_base = os.path.abspath("code.py").replace("code.py","").replace(site_base_base,"")
http_base += site_base


def header(adict):
	if adict.has_key("title"): title = " - " + adict["title"]
	else: title = ""
	return """

<head>
	<title>"""+site_title+title+"""</title>
	<LINK REL=StyleSheet HREF='"""+site_base+"""static/style.css' TYPE="text/css" MEDIA=screen>
	<LINK REL=StyleSheet HREF='"""+site_base+"""static/styles/idea.css' TYPE="text/css" MEDIA=screen>
	<LINK REL=StyleSheet HREF='"""+site_base+"""static/vfu/client/fileuploader.css' TYPE="text/css" MEDIA=screen>
	<script src='"""+site_base+"""static/vfu/client/fileuploader.js'></script>
	<script src='"""+site_base+"""static/jquery.js'></script>
	
	<style>
	body
	{
	width: 800;
	font-size: 10 px;
	}
	
	h1
	{
		font-size: 32px;
		border-style:solid;
		border-top:thick #000000;
		border-right:thick #000000;
		border-left:thick #000000;
		border-bottom:thin solid #000000;
		
	}
	.start
	{
		font-size: 25px;
		font-weight: normal;
	}
	.start-small
	{
		font-size: 10px;
		font-weight: normal
	}
	.alt
	{
		background: rgb(200,200,200);
		border-width: 0px;
		
		
	}

	td
	{
	font-size: 12px;
	padding-left: 10px;
	padding-right: 10px;
	padding-top: 3px;
	padding-bottom: 3px;
	
	
	}
	
	tr
	{
	border-width: 1px;
	border-color: red;
	}
	.sidebar
	{
		width: 150px;
		float: right; 
		text-align: right;
	}
	
	</style>
	
</head>
"""

filer = ""

def upload_stuff(fils):
	return """
	<div class="sidebar">
		click on this <br>or<br> drag file(s) here
		<div id="file-uploader">       
    		<noscript>          
        		<p>Please enable JavaScript to use file uploader.</p>
        		<!-- or put a simple form for upload here -->
    		</noscript>
         	<script>

		 		var uploader = new qq.FileUploader({
		        // pass the dom node (ex. $(selector)[0] for jQuery users)
		        element: document.getElementById('file-uploader'),
		        // path to server-side upload script
				params: {
				filer:'"""+fils+"""'
				},
		
		        action: '"""+site_base+"""sendfile/',
				onSubmit: function(id,fileName){
				},
				onComplete: function(id,fileName,responseJSON){
				$.get('"""+site_base+"""reload/"""+fils+"""', 
					function(data) {
				  		document.getElementById("files").innerHTML = data;
						console.log(responseJSON);
				});
				}
		    });
		</script>
	</div>
	</div>
	
	
"""

def pre(stuff):
	return """
	<h1><a href='"""+site_base+""" '>"""+site_title+"""</a></h1>
	<h2>"""+stuff+"""</h2>
	"""


pre2 =	"""<div id="files">"""

post = """
</div>
"""

def sorter():
	dirpath = "files"
	# get all entries in the directory w/ stats
	entries = (os.path.join(dirpath, fn) for fn in os.listdir(dirpath))
	entries = ((os.stat(path), path) for path in entries)
	# leave only regular files, insert creation date
	entries = ((stat[ST_CTIME], path)
	           for stat, path in entries if S_ISREG(stat[ST_MODE]))
	#NOTE: on Windows `ST_CTIME` is a creation date 
	#  but on Unix it could be something else
	#NOTE: use `ST_MTIME` to sort by a modification date
	return entries

def converter(thing):
	number = os.path.getsize(thing)
	out = "<td>"
	if number > 1000000000:
		out +=  str(number/1000000000.0)[0:5] + "GB" 
	elif number > 1000000:
		out += str(number/1000000.0)[0:5] + "MB" 
	elif number > 1000:
		out += str(number/1000.0)[0:5] + "kB" 
	else:
		out += str(number)[0:5] + "B"
	out = out + "</td><td>" + time.asctime(time.localtime(os.path.getctime(thing)))+"</td>"
	return out


def marker(link):
	return "<td> <a href='"+link+"'>"+link.split("/")[len(link.split("/"))-1]+"</a> </td>"+converter(link)


def getfiles(generic):
	if generic=="drops/": generic = "files"
	else: generic = "realfiles/"+generic
	try:
		files = os.listdir(generic)
	except OSError:
		web.debug("testing!")
		web.debug(commands.getoutput("mkdir "+generic))
		files = os.listdir(generic)
		
	files.sort(key=lambda x: os.path.getctime(generic+"/"+x))
	files.reverse()
	out = "<table>\n"
	style = "alt"
	for f in files:
		if f != ".htaccess":
			if style.find("alt")==0: style = ""
			else: style ="alt" 
			out += "<tr class='"+style+"'> "+marker(generic+"/"+f)+" </tr>"
	out = out + "</table>"
	return out



class reload:
	def GET(self,generic):
		web.debug(generic)
		return getfiles(generic) 

class home:
	def GET(self,generic):
		web.header('Content-Type','text/html; charset=utf-8', unique=True)
		if generic=="drops/": generic = "files"
		filer = generic
		adict = {}
		if generic.find("files") == -1: 
			out = getfiles(generic)
			adict["title"] = generic
			return header(adict) + pre("You are in the '"+generic+"' drop")+ upload_stuff(filer) +pre2+ markdown.markdown(out) + post
			
		else:
			guess = ''.join(random.choice(string.letters) for i in xrange(5))
			
			out = """Name your drop or use the handy/dandy pre-generated random string<br><span class='start'>"""+http_base+"""</span><input style="width: 200px;" type="text" class="start" id="field1" value='"""+guess+"""'><button class="start" onclick="location.href='"""+site_base+"""'+document.getElementById('field1').value">add drop</button></div>
			<div class="start-small">only letters/numbers<br>
			Safari 5+, Chrome 5+, Firefox 3.5+ (no IE)</div>
			"""
			generic = ""
			return header(adict) + pre("")+ pre2+markdown.markdown(out) + post


class sendfile:
	def GET(self,foo):
		web.debug(foo)
		
	def POST(self,foo):
		web.debug("foo="+foo)
		x = web.input()['qqfile']
		web.debug(x)
		foo = web.input()['filer'];
		web.debug()
		if foo == "": foo = "files"
		else: foo = "realfiles/"+foo
		for f in os.listdir(foo):
			if f.find(x) > -1:
				x = x.split(".")[0]+str(int(time.time()))+"."+x.split(".")[1]
		form = web.data()
		#web.debug(form)
	   	open(foo+ "/" + str(x), 'w').write(form)
		return json.dumps({"success":"true"})
		

if __name__ == "__main__":
    app.run()

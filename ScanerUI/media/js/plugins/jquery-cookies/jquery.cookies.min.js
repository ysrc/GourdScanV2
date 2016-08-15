/*!
 * jQuery Cookie Plugin v1.1
 * https://github.com/carhartl/jquery-cookie
 *
 * Copyright 2011, Klaus Hartl
 * Dual licensed under the MIT or GPL Version 2 licenses.
 * http://www.opensource.org/licenses/mit-license.php
 * http://www.opensource.org/licenses/GPL-2.0
 */
 (function(e,t){function r(e){return e}function i(e){return decodeURIComponent(e.replace(n," "))}var n=/\+/g;e.cookie=function(n,s,o){if(arguments.length>1&&(!/Object/.test(Object.prototype.toString.call(s))||s==null)){o=e.extend({},e.cookie.defaults,o);if(s==null){o.expires=-1}if(typeof o.expires==="number"){var u=o.expires,a=o.expires=new Date;a.setDate(a.getDate()+u)}s=String(s);return t.cookie=[encodeURIComponent(n),"=",o.raw?s:encodeURIComponent(s),o.expires?"; expires="+o.expires.toUTCString():"",o.path?"; path="+o.path:"",o.domain?"; domain="+o.domain:"",o.secure?"; secure":""].join("")}o=s||e.cookie.defaults||{};var f=o.raw?r:i;var l=t.cookie.split("; ");for(var c=0,h;h=l[c]&&l[c].split("=");c++){if(f(h.shift())===n){return f(h.join("="))}}return null};e.cookie.defaults={};e.removeCookie=function(t,n){if(e.cookie(t)!==undefined){e.cookie(t,"",e.extend({},n,{expires:-1}));return true}return false}})(jQuery,document)
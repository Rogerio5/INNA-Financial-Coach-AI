
(function(){
"use strict";

function run(){

const topbar=
document.querySelector(".main > .topbar") ||
document.querySelector("header.topbar");

if(!topbar){return;}

const language=
document.getElementById("sabinoLanguageSwitcher") ||
document.getElementById("languageButton") ||
document.querySelector(".language");

const profile=
document.querySelector(".topbar .profile") ||
document.querySelector(".profile");

if(language && language.parentElement!==topbar){

if(profile && profile.parentElement===topbar){
topbar.insertBefore(language,profile);
}else{
topbar.appendChild(language);
}

}

if(profile && profile.parentElement!==topbar){
topbar.appendChild(profile);
}

topbar.setAttribute(
"data-sabino-scroll-anchor-v2",
"true"
);

topbar.style.setProperty(
"position",
"absolute",
"important"
);

topbar.style.setProperty(
"transform",
"none",
"important"
);

[language,profile]
.filter(Boolean)
.forEach(function(el){

el.style.setProperty(
"position",
"static",
"important"
);

el.style.setProperty(
"transform",
"none",
"important"
);

});

}

if(document.readyState==="loading"){
document.addEventListener("DOMContentLoaded",run,{once:true});
}else{
run();
}

window.addEventListener("load",run);

[100,400,1000,2500,4000]
.forEach(function(ms){
window.setTimeout(run,ms);
});

})();


// Loader creates loading html and associated CSS and injects it into the page

function inject_css() {

    console.log("Injecting loader CSS into page")


    // This CSS left unminified so you can change the animation if you want to.
    const css = [
'div#brython_template_loading_animation {',
'  overflow: hidden;',
'  position: absolute;',
'  left:0;',
'  top:0;',
'  width: 100%;',
'  height: 100%;',
'  background-color: whitesmoke;',
'  z-index:99;',
'  opacity:0.5;',  /* so that the main UI is still visible and the end user can read instructions etc. during loading */
'  display: flex;',
'  justify-content: center;',
'  align-items: center;',
'  cursor: wait',
'}',
'',
'div#psychology {',
'    border-radius: 20px;',
'    border:4px solid;',
'    padding:20px;',
'    min-width:40%;',
'    font-size:2em;',
'    color: black;',
'}',
'',
'.pulsing {',
'    animation: pulse 2s infinite;',
'    animation-direction: alternate;',
'    animation-timing-function: linear;',
'}',
'',
'@keyframes pulse {',
'  from {opacity:0.1 }',
'  to {opacity:1}',
'}'
    ]

    document.head.insertAdjacentHTML("beforeend", '<style id="brython_template_loading_animation_css">' + css.join('\n') + '</style>')
}

(function () {  // Ensure initialization by calling anonymous function

   // Inject stylesheet for loader
   inject_css();

   // Build the loader html
   const loader = document.createElement("div");
    Object.assign(loader, {
      id: 'brython_template_loading_animation'
    })

    const psychology = document.createElement("div");
    Object.assign(psychology, {
      id: 'psychology',
       className : 'pulsing'
    })

    const loading_icon = document.createElement("i");
    Object.assign(loading_icon, {
      id: 'loading_icon',
       className : 'fa fa-circle-o-notch fa-spin fa-fw'
    })
    psychology.appendChild(loading_icon);

    const loading_message = document.createElement("span");
    Object.assign(loading_message, {
      id: 'loading_message',
    })
    loading_message.innerHTML = "...";  // An i18n placeholder
    psychology.appendChild(loading_message);

   loader.appendChild(psychology);
   document.body.appendChild(loader);

   console.log("Loader initialized.");

})();


function update_loader_message(message) {
    document.getElementById('loading_message').innerHTML = message;
    console.log(message)
}

// Add event listener to run 1x when brython is all done to remove our blocker and its css style tag.
document.addEventListener("brython_done", function (e) {
    console.log("Started loader clean up")
    var loader = document.getElementById("brython_template_loading_animation")
    var style = document.getElementById('brython_template_loading_animation_css')
    loader.parentNode.removeChild(loader);
    style.parentNode.removeChild(style);
    console.log("Finished loader clean up")
}, { once: true });

This small addon shows the window of the audio DSP. You can comfortably change the DSP compression value with a click on your remote or keyboard without navigating through various menues.

The DSP window is only showing while a movie or a video clip is running.

Simply connect the addon with a button on your remote or keyboard. To do this, create an ```adsp.xml``` in (Linux) 

    $USER/.kodi/userdata/keymaps/

or LE/CE

    /storage/.kodi/userdata/keymaps/

with this content (replace ```<myremotekey>``` with a proper code):

    <keymap>
        <global>
            <keyboard>
                <f11>RunScript(script.input.adsp)</f11>
            </keyboard>
            <remote>
                <myremotekey>RunScript(script.input.adsp)</myremotekey>
            </remote>
        </global>
    </keymap>
    
To determine which key code you have to use instead of ```<myremotekey>...</myremotekey>``` use a keymap editor addon or take a look inside the debug log of kodi. There are several methods described. The function key 'F11' is used here for the keyboard.
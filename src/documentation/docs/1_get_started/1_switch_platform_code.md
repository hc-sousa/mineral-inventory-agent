### Example: Toggle Between Mac, Windows, and Linux Code Commands

<div id="code-block">
    <div class="tab flex space-x-4 border-b border-gray-700 mb-2">
        <button class="tablinks px-4 py-2 text-gray-400 hover:text-white transition-colors duration-200 focus:outline-none" 
                onclick="openTab(event, 'Windows')"
                id="defaultOpen">
            Windows
        </button>
        <button class="tablinks px-4 py-2 text-gray-400 hover:text-white transition-colors duration-200 focus:outline-none" 
                onclick="openTab(event, 'Mac')">
            Mac
        </button>
        <button class="tablinks px-4 py-2 text-gray-400 hover:text-white transition-colors duration-200 focus:outline-none" 
                onclick="openTab(event, 'Linux')">
            Linux
        </button>
    </div>
    
    <div id="Windows" class="tabcontent hidden bg-gray-900 text-white py-1 px-4 rounded-lg border border-gray-800">
        <pre class="bg-gray-800 text-sm text-gray-200 py-2 px-4 rounded-lg overflow-x-auto">
            <code class="language-bash">
# Windows command example
echo "This is a Windows command"
            </code>
        </pre>
    </div>

    <div id="Mac" class="tabcontent hidden bg-gray-900 text-white py-1 px-4 rounded-lg border border-gray-800">
        <pre class="bg-gray-800 text-sm text-gray-200 py-2 px-4 rounded-lg overflow-x-auto">
            <code class="language-bash">
# Mac command example
echo "This is a Mac command"
            </code>
        </pre>
    </div>

    <div id="Linux" class="tabcontent hidden bg-gray-900 text-white py-1 px-4 rounded-lg border border-gray-800">
        <pre class="bg-gray-800 text-sm text-gray-200 py-2 px-4 rounded-lg overflow-x-auto">
            <code class="language-bash">
# Linux command example
echo "This is a Linux command"
            </code>
        </pre>
    </div>
</div>

This will keep the selected platform after page reload and across different pages

<div id="code-block">
    <div class="tab flex space-x-4 border-b border-gray-700 mb-2">
        <button class="tablinks px-4 py-2 text-gray-400 hover:text-white transition-colors duration-200 focus:outline-none" 
                onclick="openTab(event, 'Windows')"
                id="defaultOpen">
            Windows
        </button>
        <button class="tablinks px-4 py-2 text-gray-400 hover:text-white transition-colors duration-200 focus:outline-none" 
                onclick="openTab(event, 'Mac')">
            Mac
        </button>
        <button class="tablinks px-4 py-2 text-gray-400 hover:text-white transition-colors duration-200 focus:outline-none" 
                onclick="openTab(event, 'Linux')">
            Linux
        </button>
    </div>
    
    <div id="Windows" class="tabcontent hidden bg-gray-900 text-white py-1 px-4 rounded-lg border border-gray-800">
        <pre class="bg-gray-800 text-sm text-gray-200 py-2 px-4 rounded-lg overflow-x-auto">
            <code class="language-bash">
# Windows command example
echo "This is a Windows command"
            </code>
        </pre>
    </div>

    <div id="Mac" class="tabcontent hidden bg-gray-900 text-white py-1 px-4 rounded-lg border border-gray-800">
        <pre class="bg-gray-800 text-sm text-gray-200 py-2 px-4 rounded-lg overflow-x-auto">
            <code class="language-bash">
# Mac command example
echo "This is a Mac command"
            </code>
        </pre>
    </div>

    <div id="Linux" class="tabcontent hidden bg-gray-900 text-white py-1 px-4 rounded-lg border border-gray-800">
        <pre class="bg-gray-800 text-sm text-gray-200 py-2 px-4 rounded-lg overflow-x-auto">
            <code class="language-bash">
# Linux command example
echo "This is a Linux command"
            </code>
        </pre>
    </div>
</div>

You can change the default platform by changing the `id="defaultOpen"` attribute in the button element. For example, to set the default platform to Mac, change `id="defaultOpen"` to `id="Mac"`.

#### Change to the next page 'More Code Snippets' to make sure the selected platform is persisted.
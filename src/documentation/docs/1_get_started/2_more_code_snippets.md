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
echo "This is another Windows command"
            </code>
        </pre>
    </div>

    <div id="Mac" class="tabcontent hidden bg-gray-900 text-white py-1 px-4 rounded-lg border border-gray-800">
        <pre class="bg-gray-800 text-sm text-gray-200 py-2 px-4 rounded-lg overflow-x-auto">
            <code class="language-bash">
# Mac command example
echo "This is another Mac command"
            </code>
        </pre>
    </div>

    <div id="Linux" class="tabcontent hidden bg-gray-900 text-white py-1 px-4 rounded-lg border border-gray-800">
        <pre class="bg-gray-800 text-sm text-gray-200 py-2 px-4 rounded-lg overflow-x-auto">
            <code class="language-bash">
# Linux command example
echo "This is anoter Linux command"
            </code>
        </pre>
    </div>
</div>
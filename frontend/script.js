// ==================== Configuration ====================
const API_URL = 'http://localhost:5000/api';

// ==================== State Management ====================
let currentTab = 'blog';
let generatedContent = '';

// ==================== DOM Elements ====================
const tabs = document.querySelectorAll('.tab');
const userInput = document.getElementById('userInput');
const inputLabel = document.getElementById('inputLabel');
const generateBtn = document.getElementById('generateBtn');
const outputSection = document.getElementById('outputSection');
const output = document.getElementById('output');
const errorMessage = document.getElementById('errorMessage');
const copyBtn = document.getElementById('copyBtn');
const downloadBtn = document.getElementById('downloadBtn');

// ==================== Check Backend Connection ====================
window.addEventListener('load', async () => {
    console.log('🚀 AI Writer Frontend Loaded');
    console.log('📍 Connecting to backend:', API_URL);
    
    try {
        const response = await fetch(`${API_URL}/health`);
        
        if (!response.ok) {
            showError('⚠️ Backend server is not responding. Please start the server.');
            console.error('Backend health check failed:', response.status);
        } else {
            const data = await response.json();
            console.log('✓ Backend server connected successfully!');
            console.log('✓ Model loaded:', data.model_loaded);
            console.log('✓ Model name:', data.model_name);
            
            // Show success message briefly
            const successMsg = document.createElement('div');
            successMsg.style.cssText = 'position: fixed; top: 20px; right: 20px; background: #10b981; color: white; padding: 15px 20px; border-radius: 8px; z-index: 1000; box-shadow: 0 4px 12px rgba(0,0,0,0.15);';
            successMsg.textContent = '✓ Connected to AI Writer Backend';
            document.body.appendChild(successMsg);
            
            setTimeout(() => {
                successMsg.style.transition = 'opacity 0.5s';
                successMsg.style.opacity = '0';
                setTimeout(() => document.body.removeChild(successMsg), 500);
            }, 3000);
        }
    } catch (error) {
        showError('⚠️ Cannot connect to backend. Make sure the server is running on port 5000.');
        console.error('Connection error:', error);
    }
});

// ==================== Tab Switching Functionality ====================
tabs.forEach(tab => {
    tab.addEventListener('click', () => {
        console.log('📑 Switching to tab:', tab.dataset.tab);
        
        // Remove active class from all tabs
        tabs.forEach(t => t.classList.remove('active'));
        
        // Add active class to clicked tab
        tab.classList.add('active');
        
        // Update current tab
        currentTab = tab.dataset.tab;
        
        // Update label and placeholder based on tab
        updateInputPlaceholder(currentTab);
        
        // Clear output and errors
        clearOutput();
    });
});

// ==================== Update Input Placeholder ====================
function updateInputPlaceholder(tabType) {
    const placeholders = {
        blog: {
            label: 'Enter your blog topic:',
            placeholder: 'E.g., "The benefits of artificial intelligence in healthcare"'
        },
        email: {
            label: 'Enter email topic or requirements:',
            placeholder: 'E.g., "Meeting schedule confirmation for next week"'
        },
        copy: {
            label: 'Enter product or service to promote:',
            placeholder: 'E.g., "New AI-powered productivity app for remote teams"'
        },
        seo: {
            label: 'Enter SEO topic with keywords:',
            placeholder: 'E.g., "Digital marketing strategies 2024"'
        },
        video: {
            label: 'Enter video topic or concept:',
            placeholder: 'E.g., "How to start a successful YouTube channel"'
        },
        summarize: {
            label: 'Enter text to summarize:',
            placeholder: 'Paste the text you want to summarize here...'
        }
    };
    
    const config = placeholders[tabType] || placeholders.blog;
    inputLabel.textContent = config.label;
    userInput.placeholder = config.placeholder;
}

// ==================== Generate Content ====================
generateBtn.addEventListener('click', async () => {
    const input = userInput.value.trim();
    
    // Validate input
    if (!input) {
        showError('❌ Please enter some text to generate content');
        userInput.focus();
        return;
    }
    
    // Validate input length
    if (input.length < 3) {
        showError('❌ Input is too short. Please provide more details.');
        return;
    }
    
    if (input.length > 5000) {
        showError('❌ Input is too long. Please keep it under 5000 characters.');
        return;
    }
    
    console.log('🎯 Generating content...');
    console.log('   Type:', currentTab);
    console.log('   Input length:', input.length);
    
    // Hide previous output and errors
    clearOutput();
    
    // Show loading state
    setLoadingState(true);
    
    try {
        // Generate content
        const content = await generateAIContent(input, currentTab);
        generatedContent = content;
        showOutput(content);
        
        console.log('✓ Content generated successfully!');
        console.log('   Output length:', content.length);
        
    } catch (error) {
        console.error('❌ Generation error:', error);
        showError(error.message || 'Failed to generate content. Please try again.');
    } finally {
        // Reset button state
        setLoadingState(false);
    }
});

// ==================== Generate AI Content (API Call) ====================
async function generateAIContent(input, type) {
    try {
        console.log('📡 Sending request to backend...');
        
        const response = await fetch(`${API_URL}/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                input: input,
                type: type,
                max_length: 500,
                temperature: 0.7
            })
        });
        
        console.log('📡 Response status:', response.status);
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || data.detail || 'Failed to generate content');
        }
        
        if (data.success && data.content) {
            return data.content;
        } else {
            throw new Error('No content generated');
        }
        
    } catch (error) {
        if (error.message.includes('fetch') || error.message.includes('Failed to fetch')) {
            throw new Error('Cannot connect to server. Make sure the backend is running on port 5000.');
        }
        throw error;
    }
}

// ==================== Set Loading State ====================
function setLoadingState(isLoading) {
    generateBtn.disabled = isLoading;
    
    if (isLoading) {
        generateBtn.innerHTML = `
            <span class="btn-icon loading">⏳</span>
            <span class="btn-text">Generating...</span>
        `;
    } else {
        generateBtn.innerHTML = `
            <span class="btn-icon">✨</span>
            <span class="btn-text">Generate Content</span>
        `;
    }
}

// ==================== Show Output ====================
function showOutput(content) {
    output.textContent = content;
    outputSection.style.display = 'block';
    
    // Smooth scroll to output
    outputSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// ==================== Show Error ====================
function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
    
    // Auto hide error after 5 seconds
    setTimeout(() => {
        errorMessage.style.display = 'none';
    }, 5000);
}

// ==================== Clear Output ====================
function clearOutput() {
    outputSection.style.display = 'none';
    errorMessage.style.display = 'none';
    output.textContent = '';
}

// ==================== Copy to Clipboard ====================
copyBtn.addEventListener('click', async () => {
    try {
        await navigator.clipboard.writeText(generatedContent);
        
        // Show success feedback
        const originalText = copyBtn.innerHTML;
        copyBtn.innerHTML = '✓ Copied!';
        copyBtn.style.background = '#10b981';
        copyBtn.style.color = 'white';
        
        console.log('✓ Content copied to clipboard');
        
        setTimeout(() => {
            copyBtn.innerHTML = originalText;
            copyBtn.style.background = '';
            copyBtn.style.color = '';
        }, 2000);
        
    } catch (error) {
        console.error('Failed to copy:', error);
        showError('Failed to copy to clipboard. Please try manually selecting the text.');
    }
});

// ==================== Download Content ====================
downloadBtn.addEventListener('click', () => {
    try {
        // Create blob
        const blob = new Blob([generatedContent], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        
        // Create download link
        const a = document.createElement('a');
        a.href = url;
        
        // Generate filename with timestamp
        const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
        a.download = `ai-writer-${currentTab}-${timestamp}.txt`;
        
        // Trigger download
        document.body.appendChild(a);
        a.click();
        
        // Cleanup
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        console.log('✓ Content downloaded');
        
        // Show success feedback
        const originalText = downloadBtn.innerHTML;
        downloadBtn.innerHTML = '✓ Downloaded!';
        downloadBtn.style.background = '#10b981';
        downloadBtn.style.color = 'white';
        
        setTimeout(() => {
            downloadBtn.innerHTML = originalText;
            downloadBtn.style.background = '';
            downloadBtn.style.color = '';
        }, 2000);
        
    } catch (error) {
        console.error('Download failed:', error);
        showError('Failed to download content. Please try copying instead.');
    }
});

// ==================== Keyboard Shortcuts ====================
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + Enter to generate
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        if (!generateBtn.disabled) {
            generateBtn.click();
        }
    }
    
    // Escape to clear output
    if (e.key === 'Escape') {
        clearOutput();
    }
});

// ==================== Auto-resize Textarea ====================
userInput.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = (this.scrollHeight) + 'px';
});

// ==================== Show Character Count ====================
userInput.addEventListener('input', function() {
    const charCount = this.value.length;
    const maxChars = 5000;
    
    // Remove existing counter if present
    let counter = document.getElementById('charCounter');
    if (!counter) {
        counter = document.createElement('div');
        counter.id = 'charCounter';
        counter.style.cssText = 'text-align: right; font-size: 0.85rem; color: #64748b; margin-top: 5px;';
        this.parentElement.appendChild(counter);
    }
    
    counter.textContent = `${charCount} / ${maxChars} characters`;
    
    // Change color if near limit
    if (charCount > maxChars * 0.9) {
        counter.style.color = '#ef4444';
    } else if (charCount > maxChars * 0.7) {
        counter.style.color = '#f59e0b';
    } else {
        counter.style.color = '#64748b';
    }
});

// ==================== Development Mode Helpers ====================
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    console.log('%c🎨 AI Writer - Development Mode', 'color: #7c3aed; font-size: 16px; font-weight: bold;');
    console.log('%cBackend API:', 'font-weight: bold;', API_URL);
    console.log('%cKeyboard Shortcuts:', 'font-weight: bold;');
    console.log('  • Ctrl/Cmd + Enter: Generate content');
    console.log('  • Escape: Clear output');
    
    // Add debug panel button
    const debugBtn = document.createElement('button');
    debugBtn.textContent = '🐛';
    debugBtn.style.cssText = 'position: fixed; bottom: 20px; right: 20px; width: 50px; height: 50px; border-radius: 50%; background: #7c3aed; color: white; border: none; font-size: 20px; cursor: pointer; box-shadow: 0 4px 12px rgba(0,0,0,0.15); z-index: 1000;';
    debugBtn.title = 'Debug Info';
    
    debugBtn.addEventListener('click', () => {
        console.log('=== Debug Info ===');
        console.log('Current Tab:', currentTab);
        console.log('Input Length:', userInput.value.length);
        console.log('Generated Content Length:', generatedContent.length);
        console.log('API URL:', API_URL);
    });
    
    document.body.appendChild(debugBtn);
}

// ==================== Analytics (Optional) ====================
function trackGeneration(type, success) {
    // Add your analytics tracking here
    console.log('📊 Analytics:', { type, success, timestamp: new Date().toISOString() });
}

// ==================== Initialize ====================
console.log('✓ AI Writer Frontend initialized');
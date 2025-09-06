// Stealth.js - Advanced browser fingerprinting evasion techniques

// Remove webdriver property
Object.defineProperty(navigator, 'webdriver', {
  get: () => undefined
});

// Mock chrome object with more realistic properties
window.chrome = {
  runtime: {
    connect: function() {
      return {
        onMessage: { addListener: function() {} },
        onDisconnect: { addListener: function() {} },
        postMessage: function() {},
        disconnect: function() {}
      };
    },
    sendMessage: function() {},
    onConnect: undefined,
    onMessage: undefined
  },
  csi: function() {},
  loadTimes: function() {},
  app: {
    isInstalled: false
  },
  cast: undefined,
  crash: undefined,
  extensions: undefined,
  gcm: undefined,
  identity: undefined,
  idltest: undefined,
  languageSettings: undefined,
  management: undefined,
  mdns: undefined,
  mediaGalleries: undefined,
  networking: undefined,
  notifications: undefined,
  permissions: undefined,
  platformKeys: undefined,
  power: undefined,
  printerProvider: undefined,
  privacy: undefined,
  processes: undefined,
  proxy: undefined,
  pushMessaging: undefined,
  runtime: undefined,
  serial: undefined,
  socket: undefined,
  sockets: undefined,
  storage: undefined,
  system: undefined,
  tabs: undefined,
  topSites: undefined,
  tts: undefined,
  ttsEngine: undefined,
  usb: undefined,
  webstore: undefined
};

// Mock permissions
const originalQuery = window.navigator.permissions.query;
window.navigator.permissions.query = (parameters) => (
  parameters.name === 'notifications' ?
    Promise.resolve({ state: Notification.permission }) :
    originalQuery(parameters)
);

// Hide Puppeteer automation indicators
if (navigator.webdriver === false) {
  // Remove automation indicators from navigator
  delete navigator.__proto__.webdriver;
  
  // Mock plugins and mimeTypes with more realistic values
  if (!navigator.plugins.length) {
    Object.defineProperty(navigator, 'plugins', {
      get: () => [
        { filename: "internal-pdf-viewer", name: "Chrome PDF Plugin", description: "Portable Document Format" },
        { filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai", name: "Chrome PDF Viewer", description: "Portable Document Format" },
        { filename: "internal-nacl-plugin", name: "Native Client", description: "Native Client" }
      ]
    });
    
    Object.defineProperty(navigator, 'mimeTypes', {
      get: () => [
        { type: "application/pdf", suffixes: "pdf", description: "Portable Document Format" },
        { type: "text/pdf", suffixes: "pdf", description: "Portable Document Format" }
      ]
    });
  }
}

// Hide Chrome automation indicators
if (window.chrome && window.chrome.runtime) {
  window.chrome.runtime.onConnect = undefined;
  window.chrome.runtime.onMessage = undefined;
  
  // Mock chrome.runtime.connect
  window.chrome.runtime.connect = function() {
    return {
      onMessage: { addListener: function() {} },
      onDisconnect: { addListener: function() {} },
      postMessage: function() {},
      disconnect: function() {}
    };
  };
  
  // Mock chrome.runtime.sendMessage
  window.chrome.runtime.sendMessage = function() {};
}

// Hide headless indicators
if (/HeadlessChrome/.test(window.navigator.userAgent)) {
  Object.defineProperty(navigator, 'userAgent', {
    get: () => navigator.userAgent.replace('HeadlessChrome', 'Chrome')
  });
}

Object.defineProperty(navigator, 'platform', {
  get: () => 'Win32'
});

// Hide missing languages
Object.defineProperty(navigator, 'languages', {
  get: () => ['en-US', 'en']
});

// Hide missing memory with more realistic values
if (!window.performance.memory) {
  Object.defineProperty(window.performance, 'memory', {
    get: () => ({
      usedJSHeapSize: Math.floor(Math.random() * 10000000) + 10000000,
      totalJSHeapSize: Math.floor(Math.random() * 20000000) + 20000000,
      jsHeapSizeLimit: Math.floor(Math.random() * 2000000000) + 2000000000
    })
  });
}

// Hide missing console.debug
if (!console.debug) {
  console.debug = () => undefined;
}

// Hide missing console.exception
if (!console.exception) {
  console.exception = () => undefined;
}

// Hide missing console.table
if (!console.table) {
  console.table = () => undefined;
}

// Add missing console methods
if (!console.info) {
  console.info = console.log;
}

if (!console.warn) {
  console.warn = console.log;
}

if (!console.error) {
  console.error = console.log;
}

// Hide missing console.memory
if (!console.memory) {
  console.memory = {
    usedJSHeapSize: Math.floor(Math.random() * 10000000) + 10000000,
    totalJSHeapSize: Math.floor(Math.random() * 20000000) + 20000000,
    jsHeapSizeLimit: Math.floor(Math.random() * 2000000000) + 2000000000
  };
}

// Hide missing console.memory
Object.defineProperty(console, 'memory', {
  get: () => ({
    usedJSHeapSize: Math.floor(Math.random() * 10000000) + 10000000,
    totalJSHeapSize: Math.floor(Math.random() * 20000000) + 20000000,
    jsHeapSizeLimit: Math.floor(Math.random() * 2000000000) + 2000000000
  })
});

// Hide missing outerHeight and outerWidth
Object.defineProperty(window, 'outerHeight', {
  get: () => window.innerHeight
});

Object.defineProperty(window, 'outerWidth', {
  get: () => window.innerWidth
});

// Hide missing inner dimensions
if (!window.outerHeight) {
  window.outerHeight = window.innerHeight;
}

if (!window.outerWidth) {
  window.outerWidth = window.innerWidth;
}

// Hide missing screen properties with more realistic values
Object.defineProperty(screen, 'availLeft', {
  get: () => 0
});

Object.defineProperty(screen, 'availTop', {
  get: () => 0
});

Object.defineProperty(screen, 'availWidth', {
  get: () => screen.width
});

Object.defineProperty(screen, 'availHeight', {
  get: () => screen.height
});

Object.defineProperty(screen, 'colorDepth', {
  get: () => 24
});

Object.defineProperty(screen, 'pixelDepth', {
  get: () => 24
});

// Hide missing devicePixelRatio with realistic values
if (!window.devicePixelRatio) {
  window.devicePixelRatio = Math.random() > 0.5 ? 1 : 1.5;
}

// Hide missing onorientationchange
if (!window.onorientationchange) {
  window.onorientationchange = null;
}

// Hide missing orientation
if (!window.orientation) {
  window.orientation = 0;
}

// Hide missing localStorage and sessionStorage
if (!window.localStorage) {
  window.localStorage = {
    getItem: function() { return null; },
    setItem: function() {},
    removeItem: function() {},
    clear: function() {},
    key: function() { return null; },
    length: 0
  };
}

if (!window.sessionStorage) {
  window.sessionStorage = {
    getItem: function() { return null; },
    setItem: function() {},
    removeItem: function() {},
    clear: function() {},
    key: function() { return null; },
    length: 0
  };
}

// Hide missing indexedDB
if (!window.indexedDB) {
  window.indexedDB = {
    open: function() { return { onsuccess: null, onerror: null }; },
    deleteDatabase: function() { return { onsuccess: null, onerror: null }; },
    cmp: function() { return 0; },
    databases: function() { return Promise.resolve([]); }
  };
}

// Hide missing webgl with more advanced spoofing
if (!window.WebGLRenderingContext) {
  window.WebGLRenderingContext = function() {};
}

// Advanced WebGL fingerprinting protection
if (window.WebGLRenderingContext) {
  const getParameter = WebGLRenderingContext.prototype.getParameter;
  WebGLRenderingContext.prototype.getParameter = function(parameter) {
    // UNMASKED_VENDOR_WEBGL
    if (parameter === 37445) {
      return 'Intel Inc.';
    }
    // UNMASKED_RENDERER_WEBGL
    if (parameter === 37446) {
      return 'Intel Iris OpenGL Engine';
    }
    
    return getParameter.apply(this, [parameter]);
  };
  
  // Hide WebGL debug renderer info
  const extension = WebGLRenderingContext.prototype.getExtension;
  WebGLRenderingContext.prototype.getExtension = function(name) {
    if (name === 'WEBGL_debug_renderer_info') {
      return null;
    }
    return extension.apply(this, [name]);
  };
}

// Advanced canvas fingerprinting protection
if (window.HTMLCanvasElement) {
  const originalGetContext = HTMLCanvasElement.prototype.getContext;
  HTMLCanvasElement.prototype.getContext = function(contextType) {
    const context = originalGetContext.apply(this, [contextType]);
    
    if (contextType === '2d' && context) {
      // Add slight noise to canvas operations to prevent fingerprinting
      const originalFillText = context.fillText;
      context.fillText = function() {
        // Add tiny random offset to prevent exact pixel matching
        const args = Array.from(arguments);
        if (args.length >= 3) {
          args[1] = parseFloat(args[1]) + (Math.random() * 0.0001 - 0.00005);
          args[2] = parseFloat(args[2]) + (Math.random() * 0.0001 - 0.00005);
        }
        return originalFillText.apply(this, args);
      };
      
      // Override toDataURL to add noise
      const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
      HTMLCanvasElement.prototype.toDataURL = function() {
        const context = this.getContext('2d');
        if (context) {
          // Add a tiny random colored pixel to prevent exact matching
          context.fillStyle = `rgba(${Math.floor(Math.random() * 255)}, ${Math.floor(Math.random() * 255)}, ${Math.floor(Math.random() * 255)}, ${Math.random() * 0.001})`;
          context.fillRect(Math.random() * this.width, Math.random() * this.height, 1, 1);
        }
        return originalToDataURL.apply(this, arguments);
      };
      
      // Override getImageData to add noise
      const originalGetImageData = context.getImageData;
      context.getImageData = function() {
        const imageData = originalGetImageData.apply(this, arguments);
        // Add slight noise to image data to prevent exact matching
        const data = imageData.data;
        for (let i = 0; i < data.length; i += 4) {
          // Add tiny random noise to RGB values
          data[i] = Math.min(255, Math.max(0, data[i] + (Math.random() * 2 - 1)));
          data[i + 1] = Math.min(255, Math.max(0, data[i + 1] + (Math.random() * 2 - 1)));
          data[i + 2] = Math.min(255, Math.max(0, data[i + 2] + (Math.random() * 2 - 1)));
        }
        return imageData;
      };
    }
    
    return context;
  };
}

// Hide missing audio with advanced spoofing
if (!window.AudioContext) {
  window.AudioContext = function() {
    return {
      sampleRate: 44100,
      destination: {
        maxChannelCount: 2
      },
      createOscillator: function() {
        return {
          frequency: { value: 0 },
          type: 'sine',
          connect: function() {},
          start: function() {},
          stop: function() {},
          disconnect: function() {}
        };
      },
      createAnalyser: function() {
        return {
          fftSize: 2048,
          frequencyBinCount: 1024,
          connect: function() {},
          disconnect: function() {}
        };
      },
      close: function() { return Promise.resolve(); }
    };
  };
}

if (!window.webkitAudioContext) {
  window.webkitAudioContext = window.AudioContext;
}

// Advanced audio fingerprinting protection
if (window.OfflineAudioContext || window.webkitOfflineAudioContext) {
  const originalOfflineAudioContext = window.OfflineAudioContext || window.webkitOfflineAudioContext;
  window.OfflineAudioContext = function() {
    // Return a modified context that produces consistent results
    const context = new originalOfflineAudioContext(...arguments);
    
    // Override startRendering to return consistent results
    const originalStartRendering = context.startRendering;
    context.startRendering = function() {
      return new Promise((resolve) => {
        // Create a consistent audio buffer
        const buffer = context.createBuffer(1, 44100, 44100);
        const channelData = buffer.getChannelData(0);
        for (let i = 0; i < channelData.length; i++) {
          // Use a deterministic pattern instead of random values
          channelData[i] = Math.sin(i * 0.01) * 0.5;
        }
        resolve(buffer);
      });
    };
    
    return context;
  };
}

// Hide missing speech recognition
if (!window.SpeechRecognition) {
  window.SpeechRecognition = function() {};
}

if (!window.webkitSpeechRecognition) {
  window.webkitSpeechRecognition = function() {};
}

// Hide missing media devices
if (!window.navigator.mediaDevices) {
  window.navigator.mediaDevices = {
    enumerateDevices: function() { return Promise.resolve([]); },
    getSupportedConstraints: function() { return {}; },
    getUserMedia: function() { return Promise.reject(new Error('Permission denied')); }
  };
}

// Hide missing geolocation
if (!window.navigator.geolocation) {
  window.navigator.geolocation = {
    getCurrentPosition: function(success, error) { 
      if (error) error(new Error('Permission denied')); 
    },
    watchPosition: function(success, error) { 
      if (error) error(new Error('Permission denied')); 
      return 1;
    },
    clearWatch: function() {}
  };
}

// Hide missing vibration
if (!window.navigator.vibrate) {
  window.navigator.vibrate = function() { return false; };
}

// Hide missing battery
if (!window.navigator.getBattery) {
  window.navigator.getBattery = function() { 
    return Promise.reject(new Error('Battery API not supported')); 
  };
}

// Hide missing clipboard
if (!window.navigator.clipboard) {
  window.navigator.clipboard = {
    readText: function() { return Promise.reject(new Error('Permission denied')); },
    writeText: function() { return Promise.reject(new Error('Permission denied')); }
  };
}

// Hide missing bluetooth
if (!window.navigator.bluetooth) {
  window.navigator.bluetooth = {
    requestDevice: function() { return Promise.reject(new Error('Permission denied')); }
  };
}

// Hide missing usb
if (!window.navigator.usb) {
  window.navigator.usb = {
    requestDevice: function() { return Promise.reject(new Error('Permission denied')); }
  };
}

// Hide missing nfc
if (!window.navigator.nfc) {
  window.navigator.nfc = {
    requestAdapter: function() { return Promise.reject(new Error('Permission denied')); }
  };
}

// Add missing toString methods
if (window.chrome && window.chrome.runtime) {
  window.chrome.runtime.toString = function() {
    return "[object Object]";
  };
}

// Hide missing toString methods
if (window.chrome && window.chrome.csi) {
  window.chrome.csi.toString = function() {
    return "function csi() { [native code] }";
  };
}

if (window.chrome && window.chrome.loadTimes) {
  window.chrome.loadTimes.toString = function() {
    return "function loadTimes() { [native code] }";
  };
}

// Hide missing toString methods for plugins
if (navigator.plugins) {
  for (let i = 0; i < navigator.plugins.length; i++) {
    navigator.plugins[i].toString = function() {
      return "[object Plugin]";
    };
  }
}

// Hide missing toString methods for mimeTypes
if (navigator.mimeTypes) {
  for (let i = 0; i < navigator.mimeTypes.length; i++) {
    navigator.mimeTypes[i].toString = function() {
      return "[object MimeType]";
    };
  }
}

// Hide missing toString methods for permissions
if (window.navigator.permissions) {
  window.navigator.permissions.toString = function() {
    return "[object Permissions]";
  };
}

// Hide missing toString methods for geolocation
if (window.navigator.geolocation) {
  window.navigator.geolocation.toString = function() {
    return "[object Geolocation]";
  };
}

// Hide missing toString methods for mediaDevices
if (window.navigator.mediaDevices) {
  window.navigator.mediaDevices.toString = function() {
    return "[object MediaDevices]";
  };
}

// Advanced hardware concurrency spoofing
Object.defineProperty(navigator, 'hardwareConcurrency', {
  get: () => Math.floor(Math.random() * 8) + 2 // Random value between 2-10
});

// Advanced device memory spoofing
if (!navigator.deviceMemory) {
  Object.defineProperty(navigator, 'deviceMemory', {
    get: () => Math.floor(Math.random() * 8) + 4 // Random value between 4-12 GB
  });
}

// Advanced CPU class spoofing
if (!navigator.cpuClass) {
  Object.defineProperty(navigator, 'cpuClass', {
    get: () => 'x86_64' // Common CPU class
  });
}

// Advanced connection information spoofing
if (!navigator.connection) {
  Object.defineProperty(navigator, 'connection', {
    get: () => ({
      downlink: Math.random() * 10 + 1, // 1-11 Mbps
      effectiveType: ['4g', '3g', '2g'][Math.floor(Math.random() * 3)],
      rtt: Math.floor(Math.random() * 100) + 50, // 50-150 ms
      saveData: false
    })
  });
}

// Advanced timezone spoofing
Object.defineProperty(Intl, 'DateTimeFormat', {
  value: function() {
    const original = new Intl.DateTimeFormat(...arguments);
    const originalResolvedOptions = original.resolvedOptions;
    original.resolvedOptions = function() {
      const options = originalResolvedOptions.call(this);
      options.timeZone = 'America/New_York'; // Fixed timezone
      return options;
    };
    return original;
  }
});

// Advanced font enumeration protection
if (!window.CanvasRenderingContext2D) {
  window.CanvasRenderingContext2D = function() {};
}

// Override measureText to add slight variations
if (window.CanvasRenderingContext2D.prototype.measureText) {
  const originalMeasureText = CanvasRenderingContext2D.prototype.measureText;
  CanvasRenderingContext2D.prototype.measureText = function() {
    const result = originalMeasureText.apply(this, arguments);
    // Add slight random variation to text measurements
    if (result.width) {
      result.width += (Math.random() * 0.1 - 0.05); // ±5% variation
    }
    return result;
  };
}

// Advanced screen and viewport spoofing
Object.defineProperty(screen, 'width', {
  get: () => window.screen.availWidth || 1920
});

Object.defineProperty(screen, 'height', {
  get: () => window.screen.availHeight || 1080
});

// Advanced plugin enumeration protection
Object.defineProperty(navigator, 'plugins', {
  get: () => [
    { filename: "internal-pdf-viewer", name: "Chrome PDF Plugin", description: "Portable Document Format" },
    { filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai", name: "Chrome PDF Viewer", description: "Portable Document Format" },
    { filename: "internal-nacl-plugin", name: "Native Client", description: "Native Client" }
  ]
});
// Stealth.js - Advanced browser fingerprinting evasion techniques

// Remove webdriver property
Object.defineProperty(navigator, 'webdriver', {
  get: () => undefined
});

// Mock chrome object
window.chrome = {
  runtime: {},
  csi: function() {},
  loadTimes: function() {}
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
  
  // Mock plugins and mimeTypes
  if (!navigator.plugins.length) {
    Object.defineProperty(navigator, 'plugins', {
      get: () => [
        { filename: "internal-pdf-viewer", name: "Chrome PDF Plugin" },
        { filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai", name: "Chrome PDF Viewer" },
        { filename: "internal-nacl-plugin", name: "Native Client" }
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

// Hide missing memory
if (!window.performance.memory) {
  Object.defineProperty(window.performance, 'memory', {
    get: () => ({
      usedJSHeapSize: 1000000,
      totalJSHeapSize: 2000000,
      jsHeapSizeLimit: 4000000
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
    usedJSHeapSize: 1000000,
    totalJSHeapSize: 2000000,
    jsHeapSizeLimit: 4000000
  };
}

// Hide missing console.memory
Object.defineProperty(console, 'memory', {
  get: () => ({
    usedJSHeapSize: 1000000,
    totalJSHeapSize: 2000000,
    jsHeapSizeLimit: 4000000
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

// Hide missing screen properties
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

// Hide missing devicePixelRatio
if (!window.devicePixelRatio) {
  window.devicePixelRatio = 1;
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

// Hide missing webgl
if (!window.WebGLRenderingContext) {
  window.WebGLRenderingContext = function() {};
}

// Hide missing canvas
if (!window.HTMLCanvasElement) {
  window.HTMLCanvasElement = function() {};
}

// Hide missing audio
if (!window.AudioContext) {
  window.AudioContext = function() {};
}

if (!window.webkitAudioContext) {
  window.webkitAudioContext = function() {};
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
// Image optimization utilities
export interface ImageOptimizationOptions {
  quality?: number;
  width?: number;
  height?: number;
  format?: 'webp' | 'jpeg' | 'png';
  lazy?: boolean;
}

export class ImageOptimizer {
  private static instance: ImageOptimizer;
  private imageCache = new Map<string, string>();

  static getInstance(): ImageOptimizer {
    if (!ImageOptimizer.instance) {
      ImageOptimizer.instance = new ImageOptimizer();
    }
    return ImageOptimizer.instance;
  }

  // Generate optimized image URL
  generateOptimizedUrl(src: string, options: ImageOptimizationOptions = {}): string {
    const cacheKey = `${src}-${JSON.stringify(options)}`;

    if (this.imageCache.has(cacheKey)) {
      return this.imageCache.get(cacheKey)!;
    }

    // For now, return original src with optimization parameters
    // In production, this would connect to an image optimization service
    const optimizedSrc = this.addOptimizationParams(src, options);
    this.imageCache.set(cacheKey, optimizedSrc);

    return optimizedSrc;
  }

  private addOptimizationParams(src: string, options: ImageOptimizationOptions): string {
    const url = new URL(src, window.location.origin);
    const params = new URLSearchParams();

    if (options.quality) {
      params.set('q', options.quality.toString());
    }

    if (options.width) {
      params.set('w', options.width.toString());
    }

    if (options.height) {
      params.set('h', options.height.toString());
    }

    if (options.format) {
      params.set('f', options.format);
    }

    if (params.toString()) {
      url.search = params.toString();
    }

    return url.toString();
  }

  // Lazy loading implementation
  setupLazyLoading(): void {
    const images = document.querySelectorAll('img[data-src]');

    if ('IntersectionObserver' in window) {
      const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const img = entry.target as HTMLImageElement;
            const src = img.dataset.src;

            if (src) {
              img.src = src;
              img.classList.remove('lazy');
              img.classList.add('loaded');
              observer.unobserve(img);
            }
          }
        });
      });

      images.forEach((img) => imageObserver.observe(img));
    } else {
      // Fallback for browsers without IntersectionObserver
      images.forEach((img) => {
        const src = (img as HTMLImageElement).dataset.src;
        if (src) {
          (img as HTMLImageElement).src = src;
        }
      });
    }
  }

  // Generate responsive image sources
  generateResponsiveSources(
    src: string,
    breakpoints: number[] = [320, 640, 768, 1024, 1280, 1920]
  ): { src: string; media: string }[] {
    return breakpoints.map((width) => ({
      src: this.generateOptimizedUrl(src, { width, quality: 85 }),
      media: `(max-width: ${width}px)`
    }));
  }

  // Preload critical images
  preloadCriticalImages(images: string[]): void {
    images.forEach((src) => {
      const link = document.createElement('link');
      link.rel = 'preload';
      link.as = 'image';
      link.href = src;
      document.head.appendChild(link);
    });
  }

  // Convert image to WebP if supported
  async convertToWebP(imageSrc: string): Promise<string> {
    return new Promise((resolve) => {
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      const img = new Image();

      img.onload = () => {
        canvas.width = img.width;
        canvas.height = img.height;

        if (ctx) {
          ctx.drawImage(img, 0, 0);

          canvas.toBlob(
            (blob) => {
              if (blob) {
                const webpSrc = URL.createObjectURL(blob);
                resolve(webpSrc);
              } else {
                resolve(imageSrc);
              }
            },
            'image/webp',
            0.8
          );
        } else {
          resolve(imageSrc);
        }
      };

      img.onerror = () => resolve(imageSrc);
      img.src = imageSrc;
    });
  }
}

// Utility functions
export const isWebPSupported = (): boolean => {
  const canvas = document.createElement('canvas');
  canvas.width = 1;
  canvas.height = 1;
  return canvas.toDataURL('image/webp').indexOf('data:image/webp') === 0;
};

export const getImageDimensions = (src: string): Promise<{ width: number; height: number }> => {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve({ width: img.width, height: img.height });
    img.onerror = reject;
    img.src = src;
  });
};

export const optimizeImageSrc = (
  src: string,
  options: ImageOptimizationOptions = {}
): string => {
  return ImageOptimizer.getInstance().generateOptimizedUrl(src, options);
};
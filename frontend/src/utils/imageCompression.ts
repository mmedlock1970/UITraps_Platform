const MAX_DIMENSION = 1920;
const JPEG_QUALITY = 0.85;
const COMPRESSION_THRESHOLD_BYTES = 500 * 1024; // 500KB — don't touch small files

export async function compressImageFile(file: File): Promise<File> {
  // Only compress image files above the threshold
  if (!file.type.startsWith('image/') || file.size <= COMPRESSION_THRESHOLD_BYTES) {
    return file;
  }

  return new Promise((resolve) => {
    const img = new Image();
    const objectUrl = URL.createObjectURL(file);

    img.onload = () => {
      URL.revokeObjectURL(objectUrl);

      const { width, height } = img;
      const longestSide = Math.max(width, height);

      // If already within bounds, only re-encode if it's a large PNG
      if (longestSide <= MAX_DIMENSION && file.type === 'image/jpeg') {
        resolve(file);
        return;
      }

      // Calculate new dimensions, preserving aspect ratio
      let newWidth = width;
      let newHeight = height;
      if (longestSide > MAX_DIMENSION) {
        const scale = MAX_DIMENSION / longestSide;
        newWidth = Math.round(width * scale);
        newHeight = Math.round(height * scale);
      }

      const canvas = document.createElement('canvas');
      canvas.width = newWidth;
      canvas.height = newHeight;

      const ctx = canvas.getContext('2d')!;
      ctx.drawImage(img, 0, 0, newWidth, newHeight);

      canvas.toBlob(
        (blob) => {
          if (!blob || blob.size >= file.size) {
            // Compression made it larger or failed — use original
            resolve(file);
            return;
          }
          const compressed = new File([blob], file.name.replace(/\.\w+$/, '.jpg'), {
            type: 'image/jpeg',
            lastModified: file.lastModified,
          });
          resolve(compressed);
        },
        'image/jpeg',
        JPEG_QUALITY,
      );
    };

    img.onerror = () => {
      URL.revokeObjectURL(objectUrl);
      resolve(file); // Fall back to original on any error
    };

    img.src = objectUrl;
  });
}

export async function compressImageFiles(files: File[]): Promise<File[]> {
  return Promise.all(files.map(compressImageFile));
}

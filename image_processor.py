import numpy as np
from PIL import Image, ImageFilter, ImageEnhance, ImageOps
import random

class AdvancedImageProcessor:
    def __init__(self):
        self.available_styles = {
            'oil_painting': 'Oil Painting Effect',
            'watercolor': 'Watercolor Painting Effect', 
            'sketch': 'Pencil Sketch Effect',
            'pop_art': 'Pop Art Effect',
            'vintage': 'Vintage/Retro Effect',
            'glitch': 'Glitch Art Effect',
            'pixel_art': 'Pixel Art Effect',
            'cartoon': 'Cartoon Effect'
        }
    
    def get_available_styles(self):
        """Return list of available artistic styles"""
        return self.available_styles
    
    def process_image(self, image, style_name):
        """Main method to apply artistic style to image"""
        if style_name not in self.available_styles:
            raise ValueError(f"Style '{style_name}' not supported. Available: {list(self.available_styles.keys())}")
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Apply the selected style
        if style_name == 'oil_painting':
            return self.oil_painting_effect(image)
        elif style_name == 'watercolor':
            return self.watercolor_effect(image)
        elif style_name == 'sketch':
            return self.sketch_effect(image)
        elif style_name == 'pop_art':
            return self.pop_art_effect(image)
        elif style_name == 'vintage':
            return self.vintage_effect(image)
        elif style_name == 'glitch':
            return self.glitch_effect(image)
        elif style_name == 'pixel_art':
            return self.pixel_art_effect(image)
        elif style_name == 'cartoon':
            return self.cartoon_effect(image)
        else:
            return image
    
    def oil_painting_effect(self, image):
        """Apply oil painting effect"""
        # Apply median filter for painting look
        painted = image.filter(ImageFilter.MedianFilter(size=3))
        
        # Enhance colors and contrast
        color_enhancer = ImageEnhance.Color(painted)
        painted = color_enhancer.enhance(1.3)
        
        contrast_enhancer = ImageEnhance.Contrast(painted)
        painted = contrast_enhancer.enhance(1.2)
        
        # Add smooth texture
        painted = painted.filter(ImageFilter.SMOOTH_MORE)
        
        return painted
    
    def watercolor_effect(self, image):
        """Create watercolor painting effect"""
        # Apply blur for soft look
        blurred = image.filter(ImageFilter.GaussianBlur(2))
        
        # Enhance edges slightly
        edges = image.filter(ImageFilter.FIND_EDGES)
        edges = edges.filter(ImageFilter.GaussianBlur(1))
        
        # Blend images
        result = Image.blend(blurred, edges, 0.1)
        
        # Boost colors
        color_enhancer = ImageEnhance.Color(result)
        result = color_enhancer.enhance(1.4)
        
        return result
    
    def sketch_effect(self, image):
        """Convert image to pencil sketch"""
        # Convert to grayscale
        grayscale = image.convert('L')
        
        # Invert the image
        inverted = ImageOps.invert(grayscale)
        
        # Apply Gaussian blur
        blurred = inverted.filter(ImageFilter.GaussianBlur(radius=3))
        
        # Blend with original
        result = Image.blend(grayscale, blurred, 0.5)
        
        # Enhance contrast
        contrast_enhancer = ImageEnhance.Contrast(result)
        result = contrast_enhancer.enhance(2.0)
        
        # Convert back to RGB
        return result.convert('RGB')
    
    def pop_art_effect(self, image):
        """Apply vibrant pop art effect"""
        # Reduce color palette
        pop_art = ImageOps.posterize(image, 4)
        
        # Boost saturation
        color_enhancer = ImageEnhance.Color(pop_art)
        pop_art = color_enhancer.enhance(2.0)
        
        # Increase contrast
        contrast_enhancer = ImageEnhance.Contrast(pop_art)
        pop_art = contrast_enhancer.enhance(1.5)
        
        return pop_art
    
    def vintage_effect(self, image):
        """Apply vintage/retro photo effect"""
        # Apply sepia tone
        vintage = self._apply_sepia_tone(image)
        
        # Add vignette
        vintage = self._add_vignette(vintage, intensity=0.7)
        
        # Reduce saturation
        color_enhancer = ImageEnhance.Color(vintage)
        vintage = color_enhancer.enhance(0.8)
        
        return vintage
    
    def glitch_effect(self, image):
        """Create digital glitch art effect"""
        # Convert to numpy array
        img_array = np.array(image)
        height, width = img_array.shape[:2]
        
        # Create glitched version
        glitched = img_array.copy()
        
        # Shift red channel
        shift_x = random.randint(5, 15)
        glitched[:, :, 0] = np.roll(glitched[:, :, 0], shift_x, axis=1)
        
        # Shift blue channel
        shift_x = random.randint(-15, -5)
        glitched[:, :, 2] = np.roll(glitched[:, :, 2], shift_x, axis=1)
        
        # Add noise
        noise = np.random.randint(0, 30, (height, width))
        for i in range(3):
            glitched[:, :, i] = np.clip(glitched[:, :, i] + noise, 0, 255)
        
        return Image.fromarray(glitched.astype(np.uint8))
    
    def pixel_art_effect(self, image):
        """Convert image to pixel art style"""
        # Reduce resolution
        small_size = (image.width // 8, image.height // 8)
        pixel_art = image.resize(small_size, Image.NEAREST)
        
        # Scale back up
        pixel_art = pixel_art.resize(image.size, Image.NEAREST)
        
        # Enhance colors
        color_enhancer = ImageEnhance.Color(pixel_art)
        pixel_art = color_enhancer.enhance(1.5)
        
        return pixel_art
    
    def cartoon_effect(self, image):
        """Apply cartoon effect"""
        # Reduce colors
        cartoon = image.convert('P', palette=Image.ADAPTIVE, colors=8)
        cartoon = cartoon.convert('RGB')
        
        # Smooth the image
        cartoon = cartoon.filter(ImageFilter.SMOOTH_MORE)
        
        # Boost saturation
        color_enhancer = ImageEnhance.Color(cartoon)
        cartoon = color_enhancer.enhance(1.3)
        
        return cartoon
    
    # Helper methods
    
    def _apply_sepia_tone(self, image):
        """Apply sepia tone effect"""
        width, height = image.size
        sepia = image.copy()
        
        for y in range(height):
            for x in range(width):
                r, g, b = image.getpixel((x, y))
                
                # Sepia formula
                tr = int(0.393 * r + 0.769 * g + 0.189 * b)
                tg = int(0.349 * r + 0.686 * g + 0.168 * b)
                tb = int(0.272 * r + 0.534 * g + 0.131 * b)
                
                sepia.putpixel((x, y), (
                    min(255, tr),
                    min(255, tg), 
                    min(255, tb)
                ))
        
        return sepia
    
    def _add_vignette(self, image, intensity=0.7):
        """Add vignette (darkened edges) effect"""
        width, height = image.size
        vignette = image.copy()
        
        for y in range(height):
            for x in range(width):
                # Calculate distance from center
                dx = (x - width/2) / (width/2)
                dy = (y - height/2) / (height/2)
                distance = (dx**2 + dy**2) ** 0.5
                
                # Apply vignette
                vignette_factor = 1 - (distance * intensity)
                vignette_factor = max(0, min(1, vignette_factor))
                
                r, g, b = image.getpixel((x, y))
                vignette.putpixel((x, y), (
                    int(r * vignette_factor),
                    int(g * vignette_factor),
                    int(b * vignette_factor)
                ))
        
        return vignette

# Test the processor
if __name__ == '__main__':
    processor = AdvancedImageProcessor()
    print("✅ Image Processor Working!")
    print("Available styles:", list(processor.get_available_styles().keys()))
from PIL import Image
import numpy as np

def process_image_to_verilog_format(image_path):
    """
    Reading image and convert to verilog format
    Coordinate conversion function: (x,y) → pixel_index = y * 96 + x
    """
    # image to rgb, ensure 96x64
    img = Image.open(image_path)
    img = img.convert('RGB')    
    width, height = img.size    
    if width != 96 or height != 64:
        print(f"Warning: Invalid size: {width}x{height}")
    
    # image to numpy array
    img_array = np.array(img)
    
    # dictionary that saves pixel_index
    color_to_pixels = {}
    
    for y in range(height):
        for x in range(width):
            pixel_index = y * width + x
            r, g, b = img_array[y, x]
            r_5bit = (r >> 3) 
            g_6bit = (g >> 2)
            b_5bit = (b >> 3)

            color_str = f"16'b{r_5bit:05b}{g_6bit:06b}{b_5bit:05b}"
            # map color to pixel_index
            if color_str not in color_to_pixels:
                color_to_pixels[color_str] = []
            color_to_pixels[color_str].append(pixel_index)
    
    print(f"Found {len(color_to_pixels)} colours in the image.")
    
    # generate verilog output
    output_lines = []
    
    for i, (color, pixels) in enumerate(color_to_pixels.items()):
        pixels.sort()
        
        pixel_conditions = []
        current_range = []
        
        for pixel in pixels:
            if not current_range:
                current_range = [pixel, pixel]
            elif pixel == current_range[1] + 1:
                current_range[1] = pixel
            else:
                if current_range[0] == current_range[1]:
                    pixel_conditions.append(f"pixel_index == {current_range[0]}")
                else:
                    pixel_conditions.append(f"((pixel_index >= {current_range[0]}) && (pixel_index <= {current_range[1]}))")
                current_range = [pixel, pixel]
        
        if current_range:
            if current_range[0] == current_range[1]:
                pixel_conditions.append(f"pixel_index == {current_range[0]}")
            else:
                pixel_conditions.append(f"((pixel_index >= {current_range[0]}) && (pixel_index <= {current_range[1]}))")
        
        condition = " || ".join(pixel_conditions)
        
        if i == 0:
            line = f"if ({condition}) oled_data = {color};"
        else:
            line = f"else if ({condition}) oled_data = {color};"
        
        output_lines.append(line)
    
    return "\n".join(output_lines)

def process_image_detailed_info(image_path):

    # read image and show detailed pixel info
    img = Image.open(image_path)
    img = img.convert('RGB')
    width, height = img.size
    
    img_array = np.array(img)

    print("=== Pixel Coordinate and Index Mapping Example ===")
    print("Top-left Corner Pixels:")
    for y in range(min(3, height)):
        for x in range(min(3, width)):
            pixel_index = y * width + x
            r, g, b = img_array[y, x]
            print(f"Coordinate({x},{y}) → pixel_index = {pixel_index}, RGB = ({r},{g},{b})")

    print("\nBottom-right Corner Pixels:")
    for y in range(max(0, height-3), height):
        for x in range(max(0, width-3), width):
            pixel_index = y * width + x
            r, g, b = img_array[y, x]
            print(f"Coordinate({x},{y}) → pixel_index = {pixel_index}, RGB = ({r},{g},{b})")

    return process_image_to_verilog_format(image_path)


if __name__ == "__main__":

    image_path = "D:\_codecode\ppppppp\EE2026_FDP_project\keyboard1_final_version.png" # Insert image path here
    
    try:
        print("processing image...")
        result = process_image_detailed_info(image_path)
        
        print("\n" + "="*80 + "\n")
        print('Verilog code generated:\n')
        print(result)
        output_path = r"D:\_codecode\ppppppp\EE2026_FDP_project\output_verilog.txt"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result)
        
        print(f"\nresult saved to output_verilog.txt")
        
        # Show image info
        img = Image.open(image_path)
        width, height = img.size
        total_pixels = width * height
        print(f"\nCheck Image Info:")
        print(f"Size: {width} x {height}")
        print(f"Total pixels: {total_pixels}")
        print(f"pixel_index Rnage : 0 to {total_pixels-1}")
        print(f"Coordinate function: pixel_index = y * {width} + x")
        print(f"Coordinate range: x=[0,{width-1}], y=[0,{height-1}]")
        
    except FileNotFoundError:
        print(f"Error: unable to locate path: {image_path}")
    except Exception as e:

        print(f"Error processing image: {e}")

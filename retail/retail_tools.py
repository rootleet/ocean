from PIL import Image, ImageDraw, ImageFont


def create_recipe_card(product_name, recipe_items):
    # Set font and margin values
    font = ImageFont.load_default()
    margin = 20
    line_height = 20

    # Table Header
    header = ["NAME", "PACKING", "Quantity"]
    col_width = [150, 150, 100]

    # Calculate the table width based on the sum of column widths
    table_width = margin + sum(col_width) + margin

    # Calculate the total height needed for the content
    total_height = 4 * line_height + len(recipe_items) * line_height

    # Create a blank image with a white background
    image_width = table_width
    image_height = total_height
    image = Image.new("RGB", (image_width, image_height), "white")
    draw = ImageDraw.Draw(image)

    # Title: RECIPE CARD
    title_text = "RECIPE CARD"
    draw.text((margin, margin), title_text, fill="black", font=font)

    # PRODUCT: Product Name
    product_text = f"PRODUCT: {product_name}"
    draw.text((margin, margin + line_height), product_text, fill="black", font=font)

    # Recipe Items Table
    table_start_y = margin + 2 * line_height

    for i, header_text in enumerate(header):
        draw.rectangle(
            [margin + sum(col_width[:i]), table_start_y, margin + sum(col_width[: i + 1]), table_start_y + line_height],
            outline="black",
        )
        draw.text((margin + sum(col_width[:i]) + 5, table_start_y + 5), header_text, fill="black", font=font)

    # Table Data
    data_start_y = table_start_y + line_height

    for item in recipe_items:
        for i, value in enumerate(item):
            draw.rectangle(
                [margin + sum(col_width[:i]), data_start_y, margin + sum(col_width[: i + 1]),
                 data_start_y + line_height],
                outline="black",
            )
            draw.text((margin + sum(col_width[:i]) + 5, data_start_y + 5), str(value), fill="black", font=font)
        data_start_y += line_height

    # Save the image
    file_name = f"static/recipe_card/{product_name}.png"
    image.save(file_name)


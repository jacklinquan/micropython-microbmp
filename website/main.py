from browser import document, html, window  # type: ignore
from io import BytesIO
import base64

from microbmp import MicroBMP


def main():
    def follow_value(a, b):
        a.text = b.value

    def get_color_text():
        r = f"{int(html_label_red.text):02x}"
        g = f"{int(html_label_green.text):02x}"
        b = f"{int(html_label_blue.text):02x}"
        return f"#{r}{g}{b}"

    def get_color_nums(text):
        start = text.find("(")
        end = text.find(")")
        l = text[start + 1 : end].split(",")
        r = int(l[0].strip())
        g = int(l[1].strip())
        b = int(l[2].strip())
        return r, g, b

    def download_bmp_file(bmp_bytes, file_name="output.bmp"):
        b64 = base64.b64encode(bmp_bytes).decode("utf-8")
        data_url = f"data:image/bmp;base64,{b64}"

        a = html.A("Download", href=data_url, download=file_name)
        a.style.display = "none"
        document <= a
        a.click()
        a.remove()

    def download(event):
        img = MicroBMP(8, 8, 24)

        for y, row in enumerate(cells):
            for x, cell in enumerate(row):
                r, g, b = get_color_nums(cell.style.backgroundColor)
                img[x, y] = (r, g, b)

        bf_io = BytesIO()
        img.write_io(bf_io)
        bf_io.seek(0)

        bmp_bytes = bf_io.read()
        download_bmp_file(bmp_bytes, file_name=html_input_file_name.value)

    # Header
    document <= html.NAV(
        html.DIV(
            html.DIV("MicroBMP", Class="brand-logo center"),
            Class="nav-wrapper container center",
        ),
        Class="teal",
        role="navigation",
    )

    html_input_file_name = html.INPUT(type="text", maxlength="50", value="output.bmp")
    html_label_red = html.LABEL("0")
    html_input_red = html.INPUT(
        type="range", min="0", max="255", value=html_label_red.text
    )
    html_label_green = html.LABEL("0")
    html_input_green = html.INPUT(
        type="range", min="0", max="255", value=html_label_green.text
    )
    html_label_blue = html.LABEL("0")
    html_input_blue = html.INPUT(
        type="range", min="0", max="255", value=html_label_blue.text
    )
    html_button_download = html.BUTTON("Download")

    html_input_red.bind(
        "input", (lambda ev, a=html_label_red, b=html_input_red: follow_value(a, b))
    )
    html_input_green.bind(
        "input", (lambda ev, a=html_label_green, b=html_input_green: follow_value(a, b))
    )
    html_input_blue.bind(
        "input", (lambda ev, a=html_label_blue, b=html_input_blue: follow_value(a, b))
    )

    grid = html.DIV(id="grid")
    cells = []
    for row in range(8):
        row_cells = []
        for col in range(8):
            cell = html.DIV(Class="cell")
            cell.attrs["data-row"] = str(row)
            cell.attrs["data-col"] = str(col)
            cell.style.backgroundColor = "#ffffff"

            def toggle(ev, cell=cell):
                r, g, b = get_color_nums(cell.style.backgroundColor)
                if (r, g, b) != (255, 255, 255):
                    cell.style.backgroundColor = "#ffffff"
                else:
                    cell.style.backgroundColor = get_color_text()

            cell.bind("click", toggle)
            grid <= cell
            row_cells.append(cell)
        cells.append(row_cells)

    html_button_download.bind("click", download)

    # Leave some space
    document <= html.P()
    document <= html_input_file_name
    document <= html.P()
    document <= html.P("Red ") <= html_label_red
    document <= html_input_red
    document <= html.P()
    document <= html.P("Green ") <= html_label_green
    document <= html_input_green
    document <= html.P()
    document <= html.P("Blue ") <= html_label_blue
    document <= html_input_blue
    document <= html.P()
    document <= grid
    document <= html.P()
    document <= html_button_download
    document <= html.P()

    # Must do window.M.AutoInit() after all html being loaded!
    window.M.AutoInit()


if __name__ == "__main__":
    main()

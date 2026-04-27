from __future__ import annotations

import shutil
import subprocess
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


DESKTOP = Path(r"D:\Desktop")
REPO = Path(r"D:\Desktop\UAVM_2026")
TMP = REPO / "tmp_pairuav_build"
OUT_PDF = DESKTOP / "MC567033_LIANGYIQI.pdf"

RESULTS_RAW = TMP / "results_raw.png"
DETAILS_RAW = TMP / "details_raw.png"
LEADERBOARD_IMG = TMP / "leaderboard_bw.png"
DETAILS_IMG = TMP / "details_bw.png"

EDGE_CANDIDATES = [
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
]

RESULTS_URL = "https://www.codabench.org/competitions/15251/#/results-tab"
DETAILS_URL = "https://www.codabench.org/competitions/15251/detailed_results/670516"

PAGE_W, PAGE_H = 1654, 2339
MARGIN_X = 120
TOP_Y = 110


def get_font(bold: bool, size: int) -> ImageFont.FreeTypeFont:
    candidates = [
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\calibrib.ttf" if bold else r"C:\Windows\Fonts\calibri.ttf",
        r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


FONT_TITLE = get_font(True, 44)
FONT_H2 = get_font(True, 30)
FONT_BOLD = get_font(True, 26)
FONT_REG = get_font(False, 24)
FONT_SMALL = get_font(False, 20)


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font, max_width: int) -> list[str]:
    words = text.split()
    if not words:
        return [""]
    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        test = current + " " + word
        if draw.textlength(test, font=font) <= max_width:
            current = test
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def draw_block(draw: ImageDraw.ImageDraw, text: str, x: int, y: int, font, max_width: int, line_gap: int = 10) -> int:
    lines: list[str] = []
    for paragraph in text.split("\n"):
        if paragraph.strip():
            lines.extend(wrap_text(draw, paragraph, font, max_width))
        else:
            lines.append("")
    line_h = font.size + line_gap
    for line in lines:
        draw.text((x, y), line, fill="black", font=font)
        y += line_h
    return y


def draw_section(draw: ImageDraw.ImageDraw, title: str, body: str, x: int, y: int, max_width: int) -> int:
    draw.text((x, y), title, fill="black", font=FONT_H2)
    y += 42
    y = draw_block(draw, body, x, y, FONT_REG, max_width)
    return y + 18


def find_edge() -> Path:
    for candidate in EDGE_CANDIDATES:
        if candidate.exists():
            return candidate
    raise FileNotFoundError("Microsoft Edge was not found.")


def capture_public_pages():
    TMP.mkdir(parents=True, exist_ok=True)
    edge = find_edge()

    subprocess.run(
        [
            str(edge),
            "--headless",
            "--disable-gpu",
            "--window-size=2000,2200",
            "--virtual-time-budget=10000",
            f"--screenshot={RESULTS_RAW}",
            RESULTS_URL,
        ],
        check=True,
    )
    subprocess.run(
        [
            str(edge),
            "--headless",
            "--disable-gpu",
            "--window-size=1800,1200",
            "--virtual-time-budget=8000",
            f"--screenshot={DETAILS_RAW}",
            DETAILS_URL,
        ],
        check=True,
    )


def crop_assets():
    capture_public_pages()

    results = Image.open(RESULTS_RAW)
    leaderboard = results.crop((250, 1080, 1700, 1700))
    leaderboard = ImageOps.grayscale(leaderboard).convert("RGB")
    LEADERBOARD_IMG.parent.mkdir(parents=True, exist_ok=True)
    leaderboard.save(LEADERBOARD_IMG)

    details = Image.open(DETAILS_RAW)
    details = details.crop((250, 70, 1100, 520))
    details = ImageOps.grayscale(details).convert("RGB")
    details.save(DETAILS_IMG)


def make_page() -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGB", (PAGE_W, PAGE_H), "white")
    draw = ImageDraw.Draw(img)
    return img, draw


def build_pdf():
    crop_assets()
    pages: list[Image.Image] = []

    title = "Challenge Report, PairUAV: Last-Meter Precision Navigation for UAVs"

    page1, draw1 = make_page()
    y = TOP_Y
    y = draw_block(draw1, title, MARGIN_X, y, FONT_TITLE, PAGE_W - 2 * MARGIN_X, line_gap=12)
    y += 12
    draw1.line((MARGIN_X, y, PAGE_W - MARGIN_X, y), fill="black", width=2)
    y += 26
    y = draw_block(draw1, "Name: LIANGYIQI\nStudent ID: MC567033\nCourse: CISC7202 Practical Machine Learning", MARGIN_X, y, FONT_BOLD, PAGE_W - 2 * MARGIN_X)
    y += 16

    abstract = (
        "This report describes my solution for the PairUAV challenge. The task is to predict the relative heading angle "
        "and translation distance between a source UAV image and a target UAV image for last-meter precision navigation. "
        "I adopted the official UAVM 2026 baseline and prepared a valid Codabench submission."
    )
    y = draw_section(draw1, "1. Overview", abstract, MARGIN_X, y, PAGE_W - 2 * MARGIN_X)

    method = (
        "The official baseline uses a two-stage design. First, SuperGlue extracts sparse feature correspondences between "
        "each source-target image pair. These correspondences are converted into a two-channel matching field. Second, "
        "the RGB image and matching field are fed into a DINO-pretrained ResNet backbone through a lightweight adapter, "
        "and a regression head predicts the angle and distance."
    )
    y = draw_section(draw1, "2. Method", method, MARGIN_X, y, PAGE_W - 2 * MARGIN_X)

    implementation = (
        "I used the official UAVM_2026 repository and adapted the workflow on my local Windows machine. I prepared the "
        "submission file in the exact format required by Codabench, where the zip file contains only result.txt at the root. "
        "This allowed me to submit the baseline result directly and verify the score online."
    )
    y = draw_section(draw1, "3. Implementation", implementation, MARGIN_X, y, PAGE_W - 2 * MARGIN_X)

    result_text = (
        "My submission ID was 670516. The public Codabench result showed final_score = 0.633957, "
        "distance_rel_error = 0.988067, and angle_rel_error = 0.279847. On the public leaderboard page, "
        "my account liangyiqi appeared at rank #11 at the time of capture."
    )
    y = draw_section(draw1, "4. Result Summary", result_text, MARGIN_X, y, PAGE_W - 2 * MARGIN_X)
    pages.append(page1)

    page2, draw2 = make_page()
    y = TOP_Y
    analysis = (
        "The baseline is simple but effective because it uses geometric correspondence information instead of relying only "
        "on global appearance similarity. This is reasonable for last-meter UAV navigation, where final pose alignment is "
        "sensitive to viewpoint and local structure."
    )
    y = draw_section(draw2, "5. Analysis", analysis, MARGIN_X, y, PAGE_W - 2 * MARGIN_X)

    improvements = (
        "There are several possible ways to improve the baseline. A stronger feature fusion module may better combine image "
        "appearance and matching cues. Confidence-based filtering may also reduce the effect of poor local matches. In addition, "
        "stronger augmentation and multi-scale training may improve generalization on more difficult scenes."
    )
    y = draw_section(draw2, "6. Possible Improvements", improvements, MARGIN_X, y, PAGE_W - 2 * MARGIN_X)

    conclusion = (
        "In conclusion, I successfully reproduced the official PairUAV baseline submission workflow and obtained a valid "
        "Codabench result. This baseline provides a reproducible starting point for the challenge, and it can be further "
        "improved in future work."
    )
    y = draw_section(draw2, "7. Conclusion", conclusion, MARGIN_X, y, PAGE_W - 2 * MARGIN_X)
    pages.append(page2)

    page3, draw3 = make_page()
    y = TOP_Y
    draw3.text((MARGIN_X, y), "Appendix: Codabench Result Proof", fill="black", font=FONT_H2)
    y += 42
    y = draw_block(
        draw3,
        "The following screenshots are included as proof of the submitted result and the public leaderboard position.",
        MARGIN_X,
        y,
        FONT_REG,
        PAGE_W - 2 * MARGIN_X,
    )
    y += 20

    leaderboard = Image.open(LEADERBOARD_IMG)
    leaderboard.thumbnail((PAGE_W - 2 * MARGIN_X, 900))
    page3.paste(leaderboard, (MARGIN_X, y))
    y += leaderboard.height + 18
    y = draw_block(draw3, "Leaderboard page showing user liangyiqi at rank #11.", MARGIN_X, y, FONT_SMALL, PAGE_W - 2 * MARGIN_X)
    y += 22

    details = Image.open(DETAILS_IMG)
    details.thumbnail((PAGE_W - 2 * MARGIN_X, 520))
    page3.paste(details, (MARGIN_X, y))
    y += details.height + 18
    draw_block(draw3, "Detailed results page showing final_score = 0.633957.", MARGIN_X, y, FONT_SMALL, PAGE_W - 2 * MARGIN_X)
    pages.append(page3)

    pages[0].save(OUT_PDF, save_all=True, append_images=pages[1:], resolution=200)


def cleanup():
    if TMP.exists():
        shutil.rmtree(TMP, ignore_errors=True)


def main():
    build_pdf()
    cleanup()


if __name__ == "__main__":
    main()

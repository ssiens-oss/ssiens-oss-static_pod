"""
Book generation service - AI book/ebook generation
"""

import os
import logging
from typing import Optional
import anthropic

logger = logging.getLogger(__name__)

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")


def enqueue(job_id: int, prompt: str, output_format: str = "pdf"):
    """Enqueue book generation job"""
    logger.info(f"[BOOK] Enqueuing job {job_id}: {prompt}")
    return {"status": "queued"}


def generate(job_id: int, prompt: str, output_format: str = "pdf") -> str:
    """
    Generate AI book/ebook
    Uses Claude to generate content, then exports to PDF/EPUB
    """
    logger.info(f"[BOOK] Generating job {job_id}")

    try:
        # Step 1: Generate book content with Claude
        content = generate_book_content(prompt)

        # Step 2: Format and export
        if output_format == "pdf":
            output_url = export_to_pdf(job_id, content)
        elif output_format == "epub":
            output_url = export_to_epub(job_id, content)
        else:
            output_url = export_to_pdf(job_id, content)

        logger.info(f"[BOOK] Job {job_id} completed: {output_url}")
        return output_url

    except Exception as e:
        logger.error(f"[BOOK] Job {job_id} failed: {e}")
        raise


def generate_book_content(prompt: str) -> dict:
    """Generate book content using Claude"""
    if not ANTHROPIC_API_KEY:
        # Return mock content for testing
        return {
            "title": "Sample Book",
            "chapters": [
                {"title": "Chapter 1", "content": "This is chapter 1 content."},
                {"title": "Chapter 2", "content": "This is chapter 2 content."}
            ]
        }

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    system_prompt = """You are an expert author who creates engaging, well-structured books.
Generate complete book content based on the user's prompt.
Return your response as JSON with this structure:
{
  "title": "Book Title",
  "author": "AI Generated",
  "chapters": [
    {"title": "Chapter Title", "content": "Chapter content here..."}
  ]
}"""

    user_prompt = f"""Create a complete book based on this prompt:

{prompt}

Generate:
- A compelling title
- 5-10 chapters with substantial content (500+ words each)
- Clear chapter structure
- Engaging narrative or information

Return ONLY valid JSON."""

    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=8000,
        temperature=0.7,
        system=system_prompt,
        messages=[
            {"role": "user", "content": user_prompt}
        ]
    )

    content_text = response.content[0].text

    # Parse JSON
    import json
    if "```json" in content_text:
        content_text = content_text.split("```json")[1].split("```")[0].strip()
    elif "```" in content_text:
        content_text = content_text.split("```")[1].split("```")[0].strip()

    book_data = json.loads(content_text)

    return book_data


def export_to_pdf(job_id: int, content: dict) -> str:
    """Export book content to PDF using ReportLab"""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch

        output_path = f"/tmp/book_{job_id}.pdf"

        doc = SimpleDocTemplate(output_path, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()

        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30
        )
        story.append(Paragraph(content.get("title", "Untitled"), title_style))
        story.append(Spacer(1, 0.5 * inch))

        # Author
        story.append(Paragraph(f"By {content.get('author', 'AI Generated')}", styles['Normal']))
        story.append(PageBreak())

        # Chapters
        for chapter in content.get("chapters", []):
            # Chapter title
            story.append(Paragraph(chapter["title"], styles['Heading2']))
            story.append(Spacer(1, 0.2 * inch))

            # Chapter content
            paragraphs = chapter["content"].split("\n\n")
            for para in paragraphs:
                if para.strip():
                    story.append(Paragraph(para, styles['BodyText']))
                    story.append(Spacer(1, 0.1 * inch))

            story.append(PageBreak())

        # Build PDF
        doc.build(story)

        # Upload to CDN (S3/etc) in production
        cdn_url = f"https://cdn.maker.app/books/{job_id}.pdf"

        return cdn_url

    except ImportError:
        logger.warning("ReportLab not installed, using stub")
        return f"https://cdn.maker.app/books/{job_id}.pdf"


def export_to_epub(job_id: int, content: dict) -> str:
    """Export book content to EPUB format"""
    try:
        from ebooklib import epub

        book = epub.EpubBook()

        # Metadata
        book.set_title(content.get("title", "Untitled"))
        book.set_language('en')
        book.add_author(content.get("author", "AI Generated"))

        # Chapters
        epub_chapters = []
        for i, chapter in enumerate(content.get("chapters", [])):
            c = epub.EpubHtml(
                title=chapter["title"],
                file_name=f'chap_{i+1}.xhtml',
                lang='en'
            )
            c.content = f'<h1>{chapter["title"]}</h1><p>{chapter["content"]}</p>'
            book.add_item(c)
            epub_chapters.append(c)

        # Table of contents
        book.toc = tuple(epub_chapters)

        # Navigation
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())

        # Spine
        book.spine = ['nav'] + epub_chapters

        # Write
        output_path = f"/tmp/book_{job_id}.epub"
        epub.write_epub(output_path, book)

        cdn_url = f"https://cdn.maker.app/books/{job_id}.epub"

        return cdn_url

    except ImportError:
        logger.warning("ebooklib not installed, using stub")
        return f"https://cdn.maker.app/books/{job_id}.epub"

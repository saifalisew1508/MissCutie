from io import BytesIO
from os import path, remove
from time import time

import img2pdf
from PIL import Image
from pyrogram import filters
from pyrogram.types import Message
from pywintypes import com_error
from win32com import client


from MissCutie import pbot as app
from MissCutie.utils.errors import capture_err
from MissCutie.utils.sections import section


async def convert_image_to_pdf(documents):
    for img_path in documents:
        img = Image.open(img_path).convert("RGB")
        img.save(img_path, "JPEG", quality=100)

    pdf = BytesIO(img2pdf.convert(documents))
    pdf.name = "@MissCutieRobot Document.pdf"
    return pdf


async def convert_chm_to_pdf(file_path):
    pdf_path = file_path.replace(".chm", ".pdf")
    try:
        chm_pdf = client.Dispatch("CHM.document")
        chm_pdf.Open(file_path)
        chm_pdf.SaveAs(pdf_path, 17)  # 17 is the PDF format constant
        chm_pdf.Close()
        return pdf_path
    except com_error as e:
        print(f"Error converting CHM to PDF: {str(e)}")
        return None


async def convert_djvu_to_pdf(file_path):
    pdf_path = file_path.replace(".djvu", ".pdf")
    try:
        djvu_pdf = client.Dispatch("DjVu.DjVuCtl")
        djvu_pdf.EncodeToPDF(file_path, pdf_path)
        return pdf_path
    except com_error as e:
        print(f"Error converting DJVU to PDF: {str(e)}")
        return None


async def convert_excel_to_pdf(file_path):
    pdf_path = file_path.replace(".xlsx", ".pdf")
    try:
        excel_pdf = client.Dispatch("Excel.Application")
        excel_workbook = excel_pdf.Workbooks.Open(file_path)
        excel_workbook.ExportAsFixedFormat(0, pdf_path)  # 0 is the PDF format constant
        excel_workbook.Close()
        excel_pdf.Quit()
        return pdf_path
    except com_error as e:
        print(f"Error converting Excel to PDF: {str(e)}")
        return None


async def convert(
    main_message: Message,
    reply_messages,
    status_message: Message,
    start_time: float,
):
    m = status_message

    documents = []

    for message in reply_messages:
        if message.document:
            if message.document.mime_type.split("/")[0] != "image":
                return await m.edit("Invalid mime type!")

            if message.document.file_size > 5000000:
                return await m.edit("Size too large, ABORTED!")
            documents.append(await message.download())
        elif message.document.mime_type == "application/x-chm":
            file_path = await message.download()
            pdf_path = await convert_chm_to_pdf(file_path)
            if pdf_path:
                documents.append(pdf_path)
            else:
                return await m.edit("Error converting CHM to PDF!")
        elif message.document.mime_type == "image/vnd.djvu":
            file_path = await message.download()
            pdf_path = await convert_djvu_to_pdf(file_path)
            if pdf_path:
                documents.append(pdf_path)
            else:
                return await m.edit("Error converting DJVU to PDF!")
        elif message.document.mime_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            file_path = await message.download()
            pdf_path = await convert_excel_to_pdf(file_path)
            if pdf_path:
                documents.append(pdf_path)
            else:
                return await m.edit("Error converting Excel to PDF!")
        else:
            return await m.edit("Unsupported file format!")

    pdf = await convert_image_to_pdf(documents)
    pdf.name = "@MissCutieRobot Document.pdf"

    if len(main_message.command) >= 2:
        pdf.name = main_message.text.split(None, 1)[1]

    elapsed = round(time() - start_time, 2)

    await main_message.reply_document(
        document=pdf,
        caption=section(
            "IMG2PDF",
            body={
                "Title": pdf.name,
                "Size": f"{pdf.__sizeof__() / (10**6)}MB",
                "Pages": len(documents),
                "Took": f"{elapsed}s",
            },
        ),
    )

    await m.delete()
    pdf.close()
    for file in documents:
        if path.exists(file):
            remove(file)


@app.on_message(filters.command("pdf"))
@capture_err
async def convert_to_pdf(_, message: Message):
    reply = message.reply_to_message
    if not reply:
        return await message.reply(
            "Reply to an image (as document), CHM, DJVU, or Excel file."
        )

    m = await message.reply_text("Converting..")
    start_time = time()

    if reply.media_group_id:
        messages = await app.get_media_group(
            message.chat.id,
            reply.message_id,
        )
        return await convert(message, messages, m, start_time)

    return await convert(message, [reply], m, start_time)

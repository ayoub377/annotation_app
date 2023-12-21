import json
import os

import streamlit as st
from pdf2image import convert_from_path
from paddleocr import PaddleOCR

ocr = PaddleOCR(lang="fr", use_angle_cls=False, enable_mkldnn=True)


def load_data(output):
    for i, word_info in enumerate(output):
        word = word_info[1][0]  # Get the word
        word_bbox = word_info[0]  # Get the bounding box coordinates for the word
        # Calculate the minimum and maximum x and y coordinates for the word
        xmin = min(x for x, y in word_bbox)
        ymin = min(y for x, y in word_bbox)
        xmax = max(x for x, y in word_bbox)
        ymax = max(y for x, y in word_bbox)

        # append to the words list
        words_list.append(word)
        bboxes_list.append([xmin, ymin, xmax, ymax])

        if len(st.session_state.ner_tags_list) <= len(st.session_state.output):
            st.session_state.ner_tags_list.append('O')

        # Create a dropdown to select the NER tag for the current word
        st.write(f"{word}:")
        tag = st.selectbox(f"Select NER tag for {word}:", ner_tags_list, index=0, key=f"tag_{i}")

        # Add "Enter" and "Edit" buttons side by side using st.columns
        col1, col2 = st.columns(2)

        if col2.button(f"Modifier_{i}"):
            # Find the index of the word in the words_list and update the tag
            word_index = words_list.index(word)
            st.session_state.ner_tags_list[word_index] = tag
            st.warning("Tag Modifie!")  # Use warning to display in yellow

        if col2.button(f"Ajouter_{i}"):
            # Find the index of the word in the words_list and update the tag
            word_index = words_list.index(word)
            st.session_state.ner_tags_list[word_index] = tag
            st.warning("Tag ajoute!")  # Use warning to display in yellow


def reset():
    st.session_state.output = ""
    words_list = []
    bboxes_list = []
    st.session_state.ner_tags_list = ['O'] * len(st.session_state.output)
    id_value = ""
    st.session_state.Image_type_choice = False
    st.session_state.pdf_type_choice = False
    st.session_state.uploaded_file = None
    st.session_state.tmp_img_path = ''
    st.session_state.image_name = ""

    try:
        # Attempt to remove the file
        os.remove("data/image_1.png")
        os.remove(f"{json_file_name}.json")
        print("File removed successfully")

    except Exception as e:
        # Handle exceptions (e.g., file not found)
        print(f"Error removing file: {e}")


def set_name_image():
    filename = os.path.basename(st.session_state.input_image)
    st.session_state.image_name = filename


if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None

if 'output' not in st.session_state:
    st.session_state.output = ""

# Add a checkbox to choose between PDF and image
if st.session_state.output == '':
    st.session_state.Image_type_choice = st.checkbox("Image")
    st.session_state.pdf_type_choice = st.checkbox("PDF")

    if st.session_state.Image_type_choice:
        st.session_state.uploaded_file = st.file_uploader("Upload an image here", type=["jpg", "png", "jpeg"])

    elif st.session_state.pdf_type_choice:
        st.session_state.uploaded_file = st.file_uploader("Upload a PDF here", type=["pdf"])

    st.session_state.input_number = st.text_input("enter number of fields")

# If a file is uploaded
if st.session_state.uploaded_file is not None:
    # create the image path
    temp_path = f"temp_path.{st.session_state.uploaded_file.name.split('.')[-1]}"
    file_extension = st.session_state.uploaded_file.name.split(".")[-1].lower()

    # check that output is empty to process new image
    if st.session_state.output == "" and st.session_state.input_number:
        if file_extension == "pdf" and st.session_state.pdf_type_choice:
            with open(temp_path, "wb") as f:
                f.write(st.session_state.uploaded_file.read())

            with st.spinner("Converting PDF to images..."):
                pdf_images = convert_from_path(temp_path, fmt="png")

            with st.spinner("Performing OCR..."):
                st.session_state.tmp_img_path = "./data/image_1.png"
                img = pdf_images[0]
                img.save(st.session_state.tmp_img_path)
                result = ocr.ocr(st.session_state.tmp_img_path)
            st.session_state.output = result[0]

        else:
            st.session_state.tmp_img_path = temp_path
            # save the image path as a file
            with st.spinner("Loading ..."):
                with open(temp_path, "wb") as image_file:
                    # Assuming uploaded_file is the file object
                    image_file.write(st.session_state.uploaded_file.read())
                    # Ocr the result
                result = ocr.ocr(temp_path)
                st.session_state.output = result[0]

    if st.session_state.tmp_img_path:
        with st.sidebar:
            st.sidebar.title(f"{st.session_state.uploaded_file.name}")
            st.image(st.session_state.tmp_img_path, use_column_width=True)

    # Initialize words_list, bboxes_list, and ner_tags_list
    if 'ner_tags_list' not in st.session_state:
        st.session_state.ner_tags_list = []

    words_list = []
    bboxes_list = []

    # Define the suggested NER tags
    ner_tags_list = [
        'O', 'numero facture', 'Telephone', 'Email', "Site web", "RC", "CNSS", "TP", "Mode de paiement", 'fournisseur',
        'date facture', 'date limite', 'montant ht',
        'montant ttc', 'tva', 'prix tva', 'addresse', 'reference', "Devise", "ICE fournisseur", "IF fournisseur",
        "Condition de paiement", "informations"
    ]

    attributes = ['designation', 'quantite', 'prix unit', 'montant ht', 'taux de remise', 'Article', 'tva']

    num_iterations = int(st.session_state.input_number)
    dynamic_tags = [f'art{i} {attr}' for i in range(1, num_iterations + 1) for attr in attributes]

    # Add the dynamic tags to the existing list
    ner_tags_list.extend(dynamic_tags)

    # article(ref) , q , prix_unitaire _HT , TVA  // variante==article
    # Define the CSS style to highlight the selected tag

    selected_tag_style = """
    <style>
        .selected-tag {
            background-color: #0077FF;
            color: white;
            padding: 5px;
            border-radius: 5px;
        }
    </style>
    """

    # App title and instructions

    st.title("Annotation App")

    # Apply the custom CSS style

    st.markdown(selected_tag_style, unsafe_allow_html=True)

    st.text("Enter NER tag for each word:")
    # User input for the desired JSON file name, id, and image path
    json_file_name = st.text_input("Enter the desired JSON file name (without the extension):")
    id_value = st.text_input("Enter the id as a string:")
    image_path = st.text_input("",
                               value=f"//content//images//", on_change=set_name_image, key="input_image")

    # only enter the loop if output is empty
    if st.session_state.output != "" and st.session_state.Image_type_choice:
        load_data(st.session_state.output)

    if st.session_state.output != "" and st.session_state.pdf_type_choice:
        load_data(st.session_state.output)

    # set a finish button
    finish_button_clicked = st.button("Finish")

    # if the user clicks finish
    if finish_button_clicked:
        # check that the json fileName and image path are not empty
        if json_file_name and image_path:
            # Create a dictionary with the collected data
            data_dict = {
                "id": id_value,
                "image_path": image_path,
                "words": words_list,
                "bboxes": bboxes_list,
                "ner_tags": st.session_state.ner_tags_list
            }

            # Save the data to a JSON file with the desired name
            json_file_path = f"{json_file_name}.json"

            with open(json_file_path, "w") as json_file:
                json.dump(data_dict, json_file)

            st.write("JSON data saved to click Download button:", json_file_path)

            # create a downloading button
            st.download_button(
                label='Download Data',
                data=open(json_file_path, 'rb').read(),
                key='download_button',
                file_name=json_file_name + ".json",  # Specify the desired file name
                mime='application/json')

        elif json_file_name == "" or image_path == "":
            st.warning("please complete the json file name and image path")
            st.session_state.output = ""

        if st.session_state.image_name:
            st.download_button(
                label='Download image',
                data=open(st.session_state.tmp_img_path, 'rb').read(),
                key='download_button_image',
                file_name=f"{st.session_state.image_name}",  # Specify the desired file name
                mime='image/png')

    st.button("Reset", type="primary", on_click=reset)

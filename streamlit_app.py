import json
import os
import streamlit as st
from paddleocr import PaddleOCR


ocr = PaddleOCR(lang="fr", use_angle_cls=False, enable_mkldnn=True)

uploaded_file = st.file_uploader("Upload an image here",type=["jpg","png","jpeg"])

# If a file is uploaded
if uploaded_file is not None:
    # create the image path
    temp_path = f"temp_path.{uploaded_file.name.split(',')[-1]}"

    if 'output' not in st.session_state:
        st.session_state.output = ""

    if st.session_state.output == "":
        # save the image path as a file
        with st.spinner("Loading ..."):
            with open(temp_path, "wb") as image_file:
                image_file.write(uploaded_file.read())  # Assuming uploaded_file is the file object  
            # Ocr the result
            result = ocr.ocr(temp_path)
            st.session_state.output = result[0]
        # remove the file
        os.remove(temp_path)
        
  # Initialize words_list, bboxes_list, and ner_tags_list
    if 'ner_tags_list' not in st.session_state:
        st.session_state.ner_tags_list = []

    words_list = []
    bboxes_list = []

    # Define the suggested NER tags
    suggested_ner_tags = ['O', 'Ref', 'NumFa', 'Fourniss', 'DateFa', 'DateLim', 'TotalHT', 'TVA', 'TotalTTc', 'unitP',
                          'Qt','TVAP', 'Désignation','Adresse']
    
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
    image_path = st.text_input("",value=f"//content//images//{uploaded_file.name}")
    
    if st.session_state.output != "":
        for i, word_info in enumerate(st.session_state.output):
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
            tag = st.selectbox(f"Select NER tag for {word}:", suggested_ner_tags, index=0, key=f"tag_{i}")

            # Add "Enter" and "Edit" buttons side by side using st.columns
            col1, col2 = st.columns(2)
            
            if col2.button(f"Edit_{i}"):
                # Find the index of the word in the words_list and update the tag
                word_index = words_list.index(word)
                st.session_state.ner_tags_list[word_index] = tag 
                st.warning("Tag updated!")  # Use warning to display in yellow
            
    finish_button_clicked = st.button("Finish")

    if finish_button_clicked:

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
            json_file_path = f".\\data\\{json_file_name}.json"
            
            with open(json_file_path, "w") as json_file:
                json.dump(data_dict, json_file)

            st.write("JSON data saved to click Download button:", json_file_path)

            st.download_button(
                    label='Download Data',
                    data=open(json_file_path, 'rb').read(),
                    key='download_button',
                    file_name= json_file_name+".json",  # Specify the desired file name
                    mime='application/json')
            
        elif json_file_name == "" or image_path=="":
            st.warning("please complete the json file name and image path")
            st.session_state.output = ""

            
    if st.button("Reset", type="primary"):
                # Clear the session state variables
                words_list = []
                bboxes_list = []
                st.session_state.ner_tags_list = [ 'O' ] * len(st.session_state.output)
                id_value = ""
                st.session_state.output = ""      
import streamlit as st
import weaviate
import pandas as pd
import os
from tqdm import tqdm
from dotenv import load_dotenv
import requests
from PIL import Image
from io import BytesIO

load_dotenv()

openai_key = os.getenv("OPENAI_API_KEY")
weaviate_key = os.environ.get("WEAVIATE_API_KEY")
weaviate_url = os.environ.get("WEAVIATE_URL")


auth_config = weaviate.AuthApiKey(api_key=weaviate_key)

# Setting up client
client = weaviate.Client(
    url=weaviate_url,
    auth_client_secret=auth_config,
    additional_headers={
        "X-OpenAI-Api-Key": openai_key,  # Replace with your OpenAI key
    },
)
# Assume the functions get_semantic_results, get_vector_results, and get_hybrid_results are defined above
# Fields to be used in queries
fields = [
            "dish_ID",
            "dishName",
            "restaurantRating",
            "cuisine",
            "priceUber",
            "priceDescription",
            "restaurantName",
            "restaurantRating",
            "emoji",
            "restaurantPhone",
            "imageUber",
            "neighborhood",
            "normalizedIngredients",
            "foodHistory",
            "specificBaseAlternatives",
            "reviewCountCategory",
            "ratingCategory",
            "cleanedDiets",
            "linkUber",
            "linkDoorDash",
            "normalizedSuitableDiseaseFoodTags",
            "texture_Tags",
            "preparation_Tags",
            "feeling_Tags",
            "spice_Category",
            "sweetness_Category",
            "bitterness_Category",
            "sour_Category",
            "savory_Delicious_Category",
            "eater_ReviewDictVec",
            "infatuation_ReviewDictVec",
]

# Number of results to fetch
num_results = 50  # Update this number as needed


# Set page configuration
st.set_page_config(
    page_title="Crispy Vector Search", page_icon=":shark:", layout="wide"
)

# Custom styles for the app
st.markdown(
    """
<style>
.big-font {
    font-size:30px !important;
    font-weight: bold;
    color: #FF4B4B;
}
.streamlit-button {
    margin: 5px;
}
.search-bar {
    display: flex;
    justify-content: center;
}
.search-box {
    width: 70%;
    margin-bottom: 10px;
}
.centered {
    text-align: center;
}
</style>
""",
    unsafe_allow_html=True,
)

# Streamlit app layout
st.markdown(
    '<p class="big-font centered">Crispy Vector Search</p>', unsafe_allow_html=True
)

chicken_animation_html = """
<div id="chicken-container" style="width: 100%; overflow: hidden;">
  <div id="chicken1" style="font-size: 48px; position: absolute; animation: moveChickenLeft 40s linear infinite;">🐔</div>
  <div id="chicken2" style="font-size: 48px; position: absolute; animation: moveChickenRight 10s linear infinite; animation-delay: 5s;">🐥</div>
</div>

<style>
  @keyframes moveChickenLeft {
    0%, 100% {
      left: -50px;
    }
    50% {
      left: 100%;
    }
  }

  @keyframes moveChickenRight {
    0%, 100% {
      left: 100%;
    }
    50% {
      left: -50px;
    }
  }
</style>
"""

# Display the animation in Streamlit
st.markdown(chicken_animation_html, unsafe_allow_html=True)

# Search bar
st.markdown('<div class="search-bar">', unsafe_allow_html=True)
search_text = st.text_input(
    "",
    placeholder="Pick a dish you love!",
    key="search",
    max_chars=50,
    on_change=None,
    help=None,
    autocomplete=None,
    args=None,
    kwargs=None,
    disabled=False,
    label_visibility="collapsed",
)
st.markdown("</div>", unsafe_allow_html=True)


def get_semantic_results(text):
    response = (
        client.query.get(
            "CrispyMuffins",
            [
            "dish_ID",
            "dishName",
            "restaurantRating",
            "cuisine",
            "priceUber",
            "priceDescription",
            "restaurantName",
            "restaurantRating",
            "emoji",
            "restaurantPhone",
            "imageUber",
            "neighborhood",
            "normalizedIngredients",
            "foodHistory",
            "specificBaseAlternatives",
            "reviewCountCategory",
            "ratingCategory",
            "cleanedDiets",
            "linkUber",
            "linkDoorDash",
            "normalizedSuitableDiseaseFoodTags",
            "texture_Tags",
            "preparation_Tags",
            "feeling_Tags",
            "spice_Category",
            "sweetness_Category",
            "bitterness_Category",
            "sour_Category",
            "savory_Delicious_Category",
            "eater_ReviewDictVec",
            "infatuation_ReviewDictVec",
            ],
        )
        .with_near_text({"concepts": [text]})
        .do()
    )
    return response


# col1, col2, col3 = st.columns(3)
# with col1:
#     if st.button("Semantic Search"):
#         if search_text:
#             results = get_semantic_results(search_text)
#             st.write(results)

if search_text:
    results = get_semantic_results(search_text)
    # st.write(results)
    # # Convert the nested structure into a flat dataframe
    # food_items = results["data"]["Get"]["CrisyNYC"]

    # Convert JSON data to DataFrame
    if results:
        df = pd.json_normalize(results['data']['Get']['CrispyMuffins'])
        # st.dataframe(df)

        # Display food metrics in a grid layout using Streamlit
        def display_food_metrics(food_df):
            st.sidebar.header("Filters")

            # Replace 'None' and other non-numeric strings with NaN
            food_df["restaurantRating"] = pd.to_numeric(
                food_df["restaurantRating"], errors="coerce"
            )

            # Restaurant Rating Slider
            min_rating, max_rating = (
                food_df["restaurantRating"].min(),
                food_df["restaurantRating"].max(),
            )
            selected_rating_range = st.sidebar.slider(
                "Restaurant Rating", min_rating, max_rating, (min_rating, max_rating)
            )

            # Additional filters for the new attributes using snake_case
            # Texture Tags Filter
            texture_tags = st.sidebar.multiselect(
                "Select Texture Tags", pd.unique(food_df["texture_Tags"].dropna())
            )

            # Preparation Tags Filter
            preparation_tags = st.sidebar.multiselect(
                "Select Preparation Tags",
                pd.unique(food_df["preparation_Tags"].dropna()),
            )

            # Feeling Tags Filter
            feeling_tags = st.sidebar.multiselect(
                "Select Feeling Tags", pd.unique(food_df["feeling_Tags"].dropna())
            )

            # Spice Category Filter
            spice_category = st.sidebar.multiselect(
                "Select Spice Category", pd.unique(food_df["spice_Category"].dropna())
            )

            # Sweetness Category Filter
            sweetness_category = st.sidebar.multiselect(
                "Select Sweetness Category",
                pd.unique(food_df["sweetness_Category"].dropna()),
            )

            # Bitterness Category Filter
            bitterness_category = st.sidebar.multiselect(
                "Select Bitterness Category",
                pd.unique(food_df["bitterness_Category"].dropna()),
            )

            # Sour Category Filter
            sour_category = st.sidebar.multiselect(
                "Select Sour Category", pd.unique(food_df["sour_Category"].dropna())
            )

            # Savory Delicious Category Filter
            savory_delicious_category = st.sidebar.multiselect(
                "Select Savory/Delicious Category",
                pd.unique(food_df["savory_Delicious_Category"].dropna()),
            )
            # Apply all filters to the DataFrame
            if texture_tags:
                food_df = food_df[food_df["texture_Tags"].isin(texture_tags)]
            if preparation_tags:
                food_df = food_df[food_df["preparation_Tags"].isin(preparation_tags)]
            if feeling_tags:
                food_df = food_df[food_df["feeling_Tags"].isin(feeling_tags)]
            if spice_category:
                food_df = food_df[food_df["spice_Category"].isin(spice_category)]
            if sweetness_category:
                food_df = food_df[
                    food_df["sweetness_Category"].isin(sweetness_category)
                ]
            if bitterness_category:
                food_df = food_df[
                    food_df["bitterness_Category"].isin(bitterness_category)
                ]
            if sour_category:
                food_df = food_df[food_df["sour_Category"].isin(sour_category)]
            if savory_delicious_category:
                food_df = food_df[
                    food_df["savory_Delicious_Category"].isin(savory_delicious_category)
                ]
            col1, col2, col3 = st.columns(3)

            # Cuisine Filter in the first column
            unique_cuisines = food_df["cuisine"].unique().tolist()
            selected_cuisine = col1.selectbox(
                "Select Cuisine", ["All"] + unique_cuisines
            )

            # Disease Filter in the second column
            unique_disease = food_df["suitableDiseaseFoodTags"].unique().tolist()
            selected_disease = col2.selectbox(
                "Do you have health concerns?", ["All"] + unique_disease
            )

            # Diet Filter in the third column
            unique_diets_2 = food_df["dietTags"].unique().tolist()
            selected_diet_2 = col3.selectbox(
                "Select Your Diet More Specific", ["All"] + unique_diets_2
            )
            # Price Filter
            unique_prices = food_df["priceDescription"].unique().tolist()
            selected_price = st.sidebar.selectbox(
                "Select Price", ["All"] + unique_prices
            )

            # Price Filter
            unique_cats = food_df["reviewCountCategory"].unique().tolist()
            selected_cat = st.sidebar.selectbox(
                "Select Review Count Category", ["All"] + unique_cats
            )

            # Apply Filters
            if selected_diet_2 != "All":
                food_df = food_df[food_df["dietTags"] == selected_diet_2]

                # Apply Filters
            if selected_disease != "All":
                food_df = food_df[
                    food_df["suitableDiseaseFoodTags"] == selected_disease
                ]

            # Apply Filters
            if selected_cat != "All":
                food_df = food_df[food_df["reviewCountCategory"] == selected_cat]

            # Apply Filters
            if selected_cuisine != "All":
                food_df = food_df[food_df["cuisine"] == selected_cuisine]

            if selected_price != "All":
                food_df = food_df[food_df["priceDescription"] == selected_price]

            food_df = food_df[
                (food_df["restaurantRating"] >= selected_rating_range[0])
                & (food_df["restaurantRating"] <= selected_rating_range[1])
            ]

            num_foods = len(food_df)

            metrics_per_row = 3  # Set the number of columns per row for the grid
            num_containers = (num_foods // metrics_per_row) + (
                num_foods % metrics_per_row > 0
            )  # Round up for the grid

            food_index = 0
            for container_index in range(num_containers):
                with st.container():
                    cols = st.columns(metrics_per_row)
                    for metric_index in range(metrics_per_row):
                        if (
                            food_index < num_foods
                        ):  # Check if there are still food items left to display
                            food_info = food_df.iloc[food_index]
                            with cols[metric_index]:
                                with st.expander(
                                    f"{food_info['dishName']} ({food_info['emoji'],food_info['priceUber'],food_info['eater_ReviewDictVec'],food_info['infatuation_ReviewDictVec']}~~~{food_info['neighborhood']}",
                                    expanded=False,
                                ):
                                    uber_link = food_info["linkUber"]
                                    door_dash_link = food_info["linkDoorDash"]
                                    if uber_link and uber_link != "None":
                                        st.markdown(
                                            f"<a href='{uber_link}' target='_blank'>{food_info['dishName']}</a>",
                                            unsafe_allow_html=True,
                                        )
                                    elif door_dash_link and door_dash_link != "None":
                                        st.markdown(
                                            f"<a href='{door_dash_link}' target='_blank'>{food_info['dishName']}</a>",
                                            unsafe_allow_html=True,
                                        )
                                    else:
                                        st.write(food_info["dishName"])
                                    # Check if the image URL is valid and not "None"
                                    image_url = food_info["imageUber"]
                                    if image_url and image_url != "None":
                                        response = requests.get(image_url)

                                        if response.status_code == 200:
                                            # Open the image and display it
                                            image = Image.open(
                                                BytesIO(response.content)
                                            )
                                            st.image(image, width=230)
                                        else:
                                            st.error("Failed to load image from URL")
                                    else:
                                        st.write("No image available")
                                    st.write(f"Cuisine: {food_info['cuisine']}")
                                    st.write(f"Rating: {food_info['restaurantRating']}")
                                    st.write(f"Price: {food_info['priceUber']}")
                                    st.write(f"Ingredients: {food_info['ingredients']}")
                                    st.write(f"Phone: {food_info['restaurantPhone']}")
                                    st.write(
                                        f"Food History: {food_info['foodHistory']}"
                                    )
                                    st.write(
                                        f"Alternative Dishes: {food_info['specificBaseAlternatives']}"
                                    )

                            food_index += 1

    else:
        st.write("Please tell us what your craving")
    # Use the function in the Streamlit app
    display_food_metrics(df)

    # with col2:
    #     if st.button("Keyword Search"):
    #         if search_text:
    #             results = get_keyword_results(search_text)
    #             st.write(results)

    # with col3:
    #     if st.button("Hybrid Search"):
    #         if search_text:
    #             results = get_hybrid_results(search_text)
    #             st.write(results)

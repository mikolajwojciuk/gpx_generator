import streamlit as st
import os
import googlemaps
from gpx_generator.gpx_generator import GPXRoute
import folium
from streamlit_folium import st_folium
from datetime import timedelta

st.set_page_config(
    page_title="GPX Generator",
    page_icon="🚵🏼",
)


if "origin" not in st.session_state:
    st.session_state.origin = ""

if "destination" not in st.session_state:
    st.session_state.destination = ""

if "waypoints" not in st.session_state:
    st.session_state.waypoints = []

if "gpx_route" not in st.session_state:
    st.session_state.gmaps_client = googlemaps.Client(
        key=os.environ.get("GMAPS_API_KEY")
    )
    st.session_state.gpx_route = GPXRoute(gmaps=st.session_state.gmaps_client)

if "map_coordinates" not in st.session_state:
    st.session_state.map_coordinates = []

st.title("GPX Generator")
st.header("Generate GPX file based on Google Maps directions")


st.divider()
st.caption("From:")
st.session_state.origin = st.text_input(
    label="origin_input", placeholder="Origin", label_visibility="collapsed"
)
st.caption("To:")
st.session_state.destination = st.text_input(
    label="destination_input", placeholder="Destination", label_visibility="collapsed"
)


add_waypoints = st.checkbox("Add waypoints")

if add_waypoints:
    with st.form("Add waypoints", clear_on_submit=True):
        waypoint = st.text_input(
            label="additional_waypoint_input",
            placeholder="Additional waypoint",
            label_visibility="collapsed",
        )
        if st.form_submit_button("Add"):
            st.session_state.waypoints.append(waypoint)

st.divider()
if st.session_state.origin and st.session_state.destination:
    st.subheader(
        f"Route from :blue[{st.session_state.origin}] to :blue[{st.session_state.destination}]"
    )
    if st.session_state.waypoints:
        waypoints_text = ""
        for waypoint in st.session_state.waypoints:
            waypoints_text += waypoint.split(",")[0] + ", "
        st.write(f"Via {waypoints_text}")

    if st.button("Generate"):
        st.session_state.gpx_route.generate_directions(
            origin=st.session_state.origin,
            destination=st.session_state.destination,
            waypoints=st.session_state.waypoints,
        )

        st.session_state.map_coordinates = [
            (coordinate["lat"], coordinate["lng"])
            for coordinate in st.session_state.gpx_route.coordinates
        ]
if st.session_state.map_coordinates:
    map = folium.Map(
        location=[
            st.session_state.map_coordinates[0][0],
            st.session_state.map_coordinates[0][1],
        ],
        zoom_start=13,
    )
    folium.PolyLine(st.session_state.map_coordinates, weight=5).add_to(map)

    min_lat = min(st.session_state.map_coordinates)[0]
    max_lat = max(st.session_state.map_coordinates)[0]
    min_lng = min(st.session_state.map_coordinates)[1]
    max_lng = max(st.session_state.map_coordinates)[1]

    map.fit_bounds([[min_lat, min_lng], [max_lat, max_lng]])

    st_folium(map)

    st.subheader(
        "Distance: " + str(round(st.session_state.gpx_route.distance / 1000, 2)) + "km"
    )
    estimated_duration = timedelta(seconds=st.session_state.gpx_route.duration)
    st.subheader("Estimated duration: " + str(estimated_duration))

    st.download_button(
        label="Donwload GPX file",
        data=st.session_state.gpx_route.gpx.to_xml(),
        file_name=f"Route from {st.session_state.origin} to {st.session_state.destination}.gpx",
    )


st.markdown(
    """<div style="width:100%;text-align:center;">
                 <a href="https://www.linkedin.com/in/mikołaj-wojciuk-72956a20b" style="float:center">
                 <img src="https://content.linkedin.com/content/dam/me/business/en-us/amp/brand-site/v2/bg/LI-Bug.svg.original.svg" width="22px"></img></a>
                 </div>""",
    unsafe_allow_html=True,
)

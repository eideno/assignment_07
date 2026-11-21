"""
1_Scrape.py — Part 1: scrape the rivals' menus into one dataset.

The owner picks the cafés, clicks Scrape, and sees what came back: how much was
scraped, every row in one table, and a download of the dataset.

The scraping itself runs in a separate program (code/scrape_menus.py) that
runner.py starts for you — Streamlit and Playwright do not share a process well.
This page only asks for it and shows the result.

Test it: pytest tests/test_pipeline.py -k scrape_page
"""

import os

import pandas as pd
import streamlit as st

from rivals import CAFES, MENUS_FILE, OUR_CAFE, run_scraper

# 1. HEADING
st.title("Salt City: Scrape the Rivals")
st.markdown("Pick the cafés to scrape. Each run replaces the saved dataset.")

# 2. PICK AND SCRAPE
cafes = st.multiselect("Cafés", list(CAFES), default=list(CAFES), key="cafes")
if st.button("Scrape", key="scrape") and cafes:
    with st.spinner("A browser is visiting each café..."):
        result = run_scraper(cafes)
    if result.returncode == 0:
        lines = result.stdout.strip().splitlines()
        st.success(lines[-1] if lines else "Done.")
    else:
        st.error("The scraper failed. The Python error is below.")
        st.code(result.stderr[-2000:])

# 3. NOTHING TO SHOW YET?
if not os.path.exists(MENUS_FILE):
    st.info("No menus yet — pick the cafés and click Scrape.")
    st.stop()

# 4. THE DATASET
menus = pd.read_csv(MENUS_FILE)
theirs = menus[menus["cafe"] != OUR_CAFE]
col1, col2, col3 = st.columns(3)
col1.metric("Cafés", int(theirs["cafe"].nunique()))
col2.metric("Items", len(theirs[["cafe", "item"]].drop_duplicates()))
col3.metric("Rows", len(theirs))
st.dataframe(menus, hide_index=True)
st.download_button("Download the dataset", menus.to_csv(index=False),
                   file_name="menus.csv", mime="text/csv", key="download")

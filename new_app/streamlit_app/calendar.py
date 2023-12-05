import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from st_aggrid import AgGrid

def create_calendar():
    # Generate a sample DataFrame for demonstration purposes
    data = {'Date': pd.date_range(start='2023-01-01', end='2023-01-31')}
    calendar_df = pd.DataFrame(data)

    # Create an AG-Grid table with the Date column
    options = AgGridOptions(
        enableSorting=False,
        enableFilter=False,
        enableColResize=False,
        enableRangeSelection=True,
        suppressContextMenu=True,
        suppressCellSelection=True,
        paginationPageSize=31,
    )

    # Display the AG-Grid table in Streamlit
    AgGrid(calendar_df, options=options, height=400, key="availability_calendar")

def main():
    st.title("Availability Calendar")

    # Create and display the calendar
    create_calendar()

if __name__ == "__main__":
    main()

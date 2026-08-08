import streamlit as st


st.set_page_config(
    page_title="Attendance Tracker",
    page_icon="📚",
    layout="wide"
)


# Store courses during the current app session
if "courses" not in st.session_state:
    st.session_state.courses = []


st.title("📚 Attendance Tracker")
st.write("Track your attendance and stay above the 75% requirement.")


# -----------------------------
# Add Course
# -----------------------------

st.header("➕ Add a Course")

course_name = st.text_input(
    "Course name",
    placeholder="e.g. Compiler Design"
)

col1, col2 = st.columns(2)

with col1:
    classes_attended = st.number_input(
        "Classes attended",
        min_value=0,
        step=1
    )

with col2:
    classes_held = st.number_input(
        "Classes held",
        min_value=0,
        step=1
    )


if st.button("Add Course"):
    if not course_name:
        st.error("Please enter a course name.")
    elif classes_attended > classes_held:
        st.error("Classes attended cannot exceed classes held.")
    else:
        course = {
            "name": course_name,
            "attended": classes_attended,
            "held": classes_held
        }

        st.session_state.courses.append(course)

        st.success(f"{course_name} added successfully!")


# -----------------------------
# Current Courses
# -----------------------------

st.header("📋 Your Courses")

if st.session_state.courses:

    for index, course in enumerate(st.session_state.courses):

        st.subheader(course["name"])

        st.write(
            f"Current attendance: "
            f"{course['attended']} / {course['held']} classes"
        )

        edit_col, delete_col = st.columns(2)

        # -----------------------------
        # Edit Course
        # -----------------------------

        with edit_col:

            with st.expander("✏️ Edit Attendance"):

                new_attended = st.number_input(
                    "Classes attended",
                    min_value=0,
                    value=course["attended"],
                    step=1,
                    key=f"edit_attended_{index}"
                )

                new_held = st.number_input(
                    "Classes held",
                    min_value=0,
                    value=course["held"],
                    step=1,
                    key=f"edit_held_{index}"
                )

                if st.button(
                    "Save Changes",
                    key=f"save_{index}"
                ):

                    if new_attended > new_held:
                        st.error(
                            "Classes attended cannot exceed classes held."
                        )
                    else:
                        st.session_state.courses[index]["attended"] = new_attended
                        st.session_state.courses[index]["held"] = new_held

                        st.success("Attendance updated!")

                        st.rerun()

        # -----------------------------
        # Delete Course
        # -----------------------------

        with delete_col:

            if st.button(
                "🗑️ Delete Course",
                key=f"delete_{index}"
            ):

                st.session_state.courses.pop(index)

                st.success(
                    f"{course['name']} deleted."
                )

                st.rerun()

else:

    st.info("No courses added yet.")
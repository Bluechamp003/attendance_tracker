import streamlit as st


from supabase import create_client



st.set_page_config(
    page_title="Attendance Tracker",
    page_icon="📚",
    layout="wide"
)
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


# ============================================================
# DATA STORAGE
# ============================================================




def load_courses():

    response = (
        supabase
        .table("courses")
        .select("*")
        .order("id")
        .execute()
    )

    courses = []

    for row in response.data:
        courses.append({
            "id": row["id"],
            "name": row["name"],
            "attended": row["attended"],
            "held": row["held"],
            "classes": row["classes"]
        })

    return courses

            _
if "courses" not in st.session_state:
    st.session_state.courses = load_courses()


# ============================================================
# COMPATIBILITY FOR OLDER SAVED COURSES
# ============================================================

for course in st.session_state.courses:

    if "classes" not in course:

        course["classes"] = (
            ["Present"] * course["attended"]
            + ["Absent"] * (course["held"] - course["attended"])
        )


# ============================================================
# TITLE
# ============================================================

st.title("📚 Attendance Tracker")

st.write(
    "Track your attendance and stay above the 75% requirement."
)


# ============================================================
# ADD COURSE
# ============================================================

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
        st.error(
            "Classes attended cannot exceed classes held."
        )

    else:

        course = {
            "name": course_name,
            "attended": classes_attended,
            "held": classes_held,
            "classes": (
                ["Present"] * classes_attended
                + ["Absent"] * (classes_held - classes_attended)
            )
        }

        response = (
            supabase
            .table("courses")
            .insert({
                "name": course["name"],
                "attended": course["attended"],
                "held": course["held"],
                "classes": course["classes"]
            })
            .execute()
        )

        if response.data:

            course["id"] = response.data[0]["id"]

            st.session_state.courses.append(course)

            st.success(
                f"{course_name} added successfully!"
            )

            st.rerun()


# ============================================================
# CURRENT COURSES
# ============================================================

st.header("📋 Your Courses")


if st.session_state.courses:

    for index, course in enumerate(
        st.session_state.courses
    ):

        st.subheader(course["name"])

        attended = course["attended"]
        held = course["held"]


        # ====================================================
        # CALCULATE ATTENDANCE
        # ====================================================

        if held > 0:

            attendance_percentage = (
                attended / held
            ) * 100

        else:

            attendance_percentage = 0


        # ====================================================
        # ATTENDANCE DISPLAY
        # ====================================================

        st.metric(
            "Attendance",
            f"{attendance_percentage:.2f}%"
        )

        st.caption(
            "Minimum required attendance: 75%"
        )


        # ====================================================
        # PROGRESS BAR
        # ====================================================

        st.progress(
            min(attendance_percentage / 100, 1.0)
        )


        # ====================================================
        # 75% STATUS
        # ====================================================

        if attendance_percentage >= 75:

            st.success(
                "✅ Attendance requirement met — "
                "75% or above."
            )

        else:

            st.error(
                "⚠️ Attendance requirement NOT met — "
                "below 75%."
            )


        # ====================================================
        # CLASS COUNT
        # ====================================================

        st.write(
            f"Classes attended: **{attended} / {held}**"
        )


        # ====================================================
        # RECORD NEXT CLASS
        # ====================================================

        st.write("### 📝 Record Today's Class")


        present_col, absent_col = st.columns(2)


        with present_col:

            if st.button(
                "✅ Present",
                key=f"present_{index}"
            ):
                course["classes"].append("Present")
                course["attended"] += 1
                course["held"] += 1

                supabase.table("courses").update({
                    "attended": course["attended"],
                    "held": course["held"],
                    "classes": course["classes"]
                }).eq("id", course["id"]).execute()

                st.rerun()


        with absent_col:
            if st.button(
                "❌ Absent",
                key=f"absent_{index}"
            ):
                course["classes"].append("Absent")
                course["held"] += 1

                supabase.table("courses").update({
                    "attended": course["attended"],
                    "held": course["held"],
                    "classes": course["classes"]
                }).eq("id", course["id"]).execute()

                st.rerun()

            


        # ====================================================
        # CLASS HISTORY
        # ====================================================

        with st.expander("📋 View Class History"):

            if course["classes"]:

                for class_number, status in enumerate(
                    course["classes"],
                    start=1
                ):

                    if status == "Present":

                        st.write(
                            f"Class {class_number}: "
                            "✅ Present"
                        )

                    else:

                        st.write(
                            f"Class {class_number}: "
                            "❌ Absent"
                        )

            else:

                st.info(
                    "No classes recorded yet."
                )


        # ====================================================
        # 75% ATTENDANCE PLANNING
        # ====================================================

        if held > 0:

            if attendance_percentage >= 75:

                classes_can_miss = int(
                    (attended / 0.75) - held
                )


                if classes_can_miss > 0:

                    st.info(
                        f"📅 You can miss "
                        f"**{classes_can_miss}** more "
                        f"class"
                        f"{'es' if classes_can_miss != 1 else ''} "
                        "and remain at or above 75%."
                    )

                else:

                    st.info(
                        "⚠️ You cannot miss your next "
                        "class if you want to stay at "
                        "or above 75%."
                    )


            else:

                classes_needed = 0


                while (
                    (attended + classes_needed)
                    / (held + classes_needed)
                    < 0.75
                ):

                    classes_needed += 1


                st.warning(
                    f"📚 You need to attend "
                    f"**{classes_needed}** consecutive "
                    f"class"
                    f"{'es' if classes_needed != 1 else ''} "
                    "to reach 75%."
                )


        # ====================================================
        # EDIT AND DELETE
        # ====================================================

        edit_col, delete_col = st.columns(2)


        # ====================================================
        # EDIT COURSE
        # ====================================================

        with edit_col:

            with st.expander("✏️ Edit Attendance"):

                new_attended = st.number_input(
                    "Classes attended",
                    min_value=0,
                    value=int(attended),
                    step=1,
                    key=f"edit_attended_{index}"
                )


                new_held = st.number_input(
                    "Classes held",
                    min_value=0,
                    value=int(held),
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

                        updated_classes = (
                            ["Present"] * new_attended
                            + ["Absent"] * (new_held - new_attended)
                        )

                        supabase.table("courses").update({
                            "attended": new_attended,
                            "held": new_held,
                            "classes": updated_classes
                        }).eq("id", course["id"]).execute()

                        st.session_state.courses[index]["attended"] = new_attended
                        st.session_state.courses[index]["held"] = new_held
                        st.session_state.courses[index]["classes"] = updated_classes

                        st.success("Attendance updated!")

                        st.rerun()


                

                # ====================================================
                # RESET COURSE
                # ====================================================

                if st.button(
                    "🔄 Reset Attendance",
                    key=f"reset_{index}"
                ):

                    st.session_state.courses[index][
                        "attended"
                    ] = 0


                    st.session_state.courses[index][
                        "held"
                    ] = 0


                    st.session_state.courses[index][
                        "classes"
                    ] = []


                    


                    st.success(
                        "Attendance reset."
                    )


                    st.rerun()


        # ====================================================
        # DELETE COURSE
        # ====================================================

        with delete_col:
            if st.button(
                "🗑️ Delete Course",
                key=f"delete_{index}"
            ):

                supabase.table("courses") \
                    .delete() \
                    .eq("id", course["id"]) \
                    .execute()

                st.session_state.courses.pop(index)

                st.success(
                    f"{course['name']} deleted."
                )

                st.rerun()

            

else:

    st.info(
        "No courses added yet."
    )
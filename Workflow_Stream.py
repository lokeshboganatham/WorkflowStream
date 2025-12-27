import streamlit as st
import pandas as pd
import os
from datetime import datetime
import json

# Page configuration
st.set_page_config(
    page_title="Workflow Management System",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1f4e79, #2e5984);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .workflow-step {
        border: 2px solid #e0e0e0;
        border-radius: 8px;
        padding: 12px;
        margin: 8px 0;
        background: black;
        font-color: #000000;
    }
    .step-completed {
        border-color: #28a745;
        background-color: #0e1117;
        font-color: #000000;
    }
    .step-not-started {
        border-color: #6c757d;
        background-color: #0e1117;
        font-color: #000000;
        opacity: 0.7;
    }
    .step-header {
        font-weight: bold;
        font-size: 1.0em;
        font-color: #000000;
        margin-bottom: 8px;
        line-height: 1.3;
    }
    .role-badge {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 0.8em;
        font-weight: bold;
        font-color: #000000;
        margin: 2px;
    }
    .role-lead { background-color: #dc3545; color: grey; }
    .role-manager { background-color: #fd7e14; color: grey; }
    .role-developer { background-color: #007bff; color: grey; }
    .role-business { background-color: #28a745; color: grey; }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    .metric-card {
        background: grey;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1f4e79;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'selected_record' not in st.session_state:
    st.session_state.selected_record = None

class WorkflowManager:
    def __init__(self):
        self.data_file = "workflow_data.xlsx"
        self.ensure_excel_file_exists()
        
    def ensure_excel_file_exists(self):
        """Create Excel file with required sheets if it doesn't exist or is missing sheets"""
        create_new_file = False
        
        if not os.path.exists(self.data_file):
            create_new_file = True
        else:
            # Check if all required sheets exist
            try:
                with pd.ExcelFile(self.data_file) as xls:
                    required_sheets = ['Records', 'Users', 'Steps']
                    existing_sheets = xls.sheet_names
                    missing_sheets = [sheet for sheet in required_sheets if sheet not in existing_sheets]
                    
                    if missing_sheets:
                        st.warning(f"Missing sheets in Excel file: {missing_sheets}. Recreating file...")
                        create_new_file = True
            except Exception as e:
                st.error(f"Error reading Excel file: {e}. Recreating file...")
                create_new_file = True
        
        if create_new_file:
            # Create default data structure
            workflow_data = pd.DataFrame(columns=[
                'Unique_ID', 'Client_Group', 'Legal_Entity', 'Solution', 'Created_Date', 'Created_By'
            ])
            
            users_data = pd.DataFrame({
                'Username': ['admin', 'john.doe', 'jane.smith', 'bob.wilson'],
                'Role': ['Lead', 'Developer', 'Manager', 'Business'],
                'Email': ['admin@company.com', 'john@company.com', 'jane@company.com', 'bob@company.com']
            })
            
            # Default workflow steps
            workflow_steps = pd.DataFrame({
                'Step_ID': list(range(1, 14)),
                'Header': ['Initiation', 'Kickoff', 'Development', 'Development', 'Development', 
                          'Review', 'Testing', 'Testing', 'Documentation', 'Documentation', 
                          'Delivery', 'Methodology', 'Presentation'],
                'Step_Name': [
                    'Identification call with ET along with impact and savings on the engagement, project code',
                    'Data received and communication of objectives to be built',
                    'Development of analytical solution',
                    'Draft output shared with ET',
                    'Output confirmed by ET',
                    'Workflow walkthrough with Lead',
                    'Testing of the workflow',
                    'Review and approval of testing document',
                    'Preparation of know your analytical solution documentation',
                    'Review of the documentation',
                    'Rolling out the email of Analytics and documentation',
                    'Methodology Approval',
                    'Visualization of results and presentation'
                ],
                'Required_Role': ['Any', 'Any', 'Any', 'Any', 'Any', 'Lead', 'Any', 'Any', 'Any', 
                                 'Manager', 'Manager', 'Lead', 'Any'],
                'Attachment_Required': [False, False, False, False, True, False, False, False, False, 
                                      False, False, True, False],
                'Optional': [False, False, False, False, False, False, False, False, False, 
                           False, False, False, True]
            })
            
            # Create empty workflow status sheet
            workflow_status = pd.DataFrame(columns=[
                'Unique_ID', 'Step_ID', 'Status', 'Assigned_To', 'Completed_By', 
                'Completed_Date', 'Comments', 'Attachment_Path'
            ])
            
            try:
                with pd.ExcelWriter(self.data_file, engine='openpyxl') as writer:
                    workflow_data.to_excel(writer, sheet_name='Records', index=False)
                    users_data.to_excel(writer, sheet_name='Users', index=False)
                    workflow_steps.to_excel(writer, sheet_name='Steps', index=False)
                    workflow_status.to_excel(writer, sheet_name='Workflow_Status', index=False)
                st.success(f"Excel file '{self.data_file}' created successfully with all required sheets!")
            except Exception as e:
                st.error(f"Failed to create Excel file: {e}")
                raise
    
    def load_data(self):
        """Load data from Excel file"""
        try:
            # Ensure file exists with all required sheets
            self.ensure_excel_file_exists()
            
            records = pd.read_excel(self.data_file, sheet_name='Records')
            users = pd.read_excel(self.data_file, sheet_name='Users')
            steps = pd.read_excel(self.data_file, sheet_name='Steps')
            
            # Load workflow status if exists
            try:
                workflow_status = pd.read_excel(self.data_file, sheet_name='Workflow_Status')
            except:
                # Create empty workflow status DataFrame if sheet doesn't exist
                workflow_status = pd.DataFrame(columns=[
                    'Unique_ID', 'Step_ID', 'Status', 'Assigned_To', 'Completed_By', 
                    'Completed_Date', 'Comments', 'Attachment_Path'
                ])
                # Save the empty sheet
                self.save_workflow_status_sheet(workflow_status)
            
            return records, users, steps, workflow_status
        except Exception as e:
            st.error(f"Error loading data: {e}")
            st.info("Please try refreshing the page. If the error persists, delete the workflow_data.xlsx file and restart the application.")
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    
    def save_workflow_status_sheet(self, workflow_status):
        """Save only the workflow status sheet"""
        try:
            # Load existing data
            with pd.ExcelFile(self.data_file) as xls:
                records = pd.read_excel(xls, sheet_name='Records')
                users = pd.read_excel(xls, sheet_name='Users')
                steps = pd.read_excel(xls, sheet_name='Steps')
            
            # Save all sheets including the new workflow status
            with pd.ExcelWriter(self.data_file, engine='openpyxl') as writer:
                records.to_excel(writer, sheet_name='Records', index=False)
                users.to_excel(writer, sheet_name='Users', index=False)
                steps.to_excel(writer, sheet_name='Steps', index=False)
                workflow_status.to_excel(writer, sheet_name='Workflow_Status', index=False)
        except Exception as e:
            st.error(f"Error saving workflow status: {e}")
    
    def save_data(self, records, users, steps, workflow_status):
        """Save data to Excel file"""
        try:
            with pd.ExcelWriter(self.data_file, engine='openpyxl') as writer:
                records.to_excel(writer, sheet_name='Records', index=False)
                users.to_excel(writer, sheet_name='Users', index=False)
                steps.to_excel(writer, sheet_name='Steps', index=False)
                workflow_status.to_excel(writer, sheet_name='Workflow_Status', index=False)
            return True
        except Exception as e:
            st.error(f"Error saving data: {e}")
            return False
    
    def get_next_unique_id(self, records):
        """Generate next unique ID starting from 1000"""
        if records.empty:
            return 1000
        return records['Unique_ID'].max() + 1
    
    def create_record(self, client_group, legal_entity, solution, created_by):
        """Create a new workflow record"""
        records, users, steps, workflow_status = self.load_data()
        
        new_id = self.get_next_unique_id(records)
        new_record = pd.DataFrame({
            'Unique_ID': [new_id],
            'Client_Group': [client_group],
            'Legal_Entity': [legal_entity],
            'Solution': [solution],
            'Created_Date': [datetime.now()],
            'Created_By': [created_by]
        })
        
        records = pd.concat([records, new_record], ignore_index=True)
        
        # Initialize workflow status for all steps
        for _, step in steps.iterrows():
            new_status = pd.DataFrame({
                'Unique_ID': [new_id],
                'Step_ID': [step['Step_ID']],
                'Status': ['Not Started'],
                'Assigned_To': [''],
                'Completed_By': [''],
                'Completed_Date': [''],
                'Comments': [''],
                'Attachment_Path': ['']
            })
            workflow_status = pd.concat([workflow_status, new_status], ignore_index=True)
        
        if self.save_data(records, users, steps, workflow_status):
            return new_id
        return None

def user_authentication():
    """Simple user authentication"""
    st.sidebar.header("👤 User Authentication")
    
    wm = WorkflowManager()
    _, users, _, _ = wm.load_data()
    
    if users.empty:
        st.sidebar.error("No users found. Please check the Excel file.")
        return None
    
    username = st.sidebar.selectbox("Select User", [""] + users['Username'].tolist())
    
    if username:
        user_info = users[users['Username'] == username].iloc[0]
        st.sidebar.success(f"Logged in as: {username}")
        st.sidebar.info(f"Role: {user_info['Role']}")
        return user_info
    
    return None

def record_management_page():
    """Page for creating and selecting records"""
    st.markdown('<div class="main-header"><h1>📋 Workflow Management System</h1></div>', 
                unsafe_allow_html=True)
    
    wm = WorkflowManager()
    records, users, steps, workflow_status = wm.load_data()
    
    tab1, tab2 = st.tabs(["Create New Record", "Select Existing Record"])
    
    with tab1:
        st.header("Create New Workflow Record")
        
        col1, col2 = st.columns(2)
        
        with col1:
            client_group = st.text_input("Client Group*")
            solution = st.text_input("Solution*")
        
        with col2:
            legal_entity = st.text_input("Legal Entity*")
        
        if st.button("Create Record", type="primary"):
            if client_group and legal_entity and solution and st.session_state.current_user is not None:
                new_id = wm.create_record(client_group, legal_entity, solution, 
                                        st.session_state.current_user['Username'])
                if new_id:
                    st.success(f"Record created successfully! Unique ID: {new_id}")
                    st.rerun()
                else:
                    st.error("Failed to create record")
            else:
                st.error("Please fill all required fields and ensure you are logged in")
    
    with tab2:
        st.header("Select Workflow Record")
        
        if not records.empty:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                unique_ids = [""] + records['Unique_ID'].astype(str).tolist()
                selected_id = st.selectbox("Unique ID", unique_ids)
            
            with col2:
                client_groups = [""] + sorted(records['Client_Group'].unique().tolist())
                selected_client = st.selectbox("Client Group", client_groups)
            
            # Filter legal entities based on client group
            if selected_client:
                filtered_entities = records[records['Client_Group'] == selected_client]['Legal_Entity'].unique()
                legal_entities = [""] + sorted(filtered_entities.tolist())
            else:
                legal_entities = [""] + sorted(records['Legal_Entity'].unique().tolist())
            
            with col3:
                selected_entity = st.selectbox("Legal Entity", legal_entities)
            
            # Filter solutions based on client group and legal entity
            filtered_records = records.copy()
            if selected_client:
                filtered_records = filtered_records[filtered_records['Client_Group'] == selected_client]
            if selected_entity:
                filtered_records = filtered_records[filtered_records['Legal_Entity'] == selected_entity]
            
            solutions = [""] + sorted(filtered_records['Solution'].unique().tolist())
            
            with col4:
                selected_solution = st.selectbox("Solution", solutions)
            
            # Find matching records
            search_records = records.copy()
            
            if selected_id:
                search_records = search_records[search_records['Unique_ID'].astype(str) == selected_id]
            if selected_client:
                search_records = search_records[search_records['Client_Group'] == selected_client]
            if selected_entity:
                search_records = search_records[search_records['Legal_Entity'] == selected_entity]
            if selected_solution:
                search_records = search_records[search_records['Solution'] == selected_solution]
            
            if not search_records.empty:
                st.subheader("Matching Records")
                for _, record in search_records.iterrows():
                    col_a, col_b = st.columns([3, 1])
                    with col_a:
                        st.info(f"ID: {record['Unique_ID']} | Client: {record['Client_Group']} | Entity: {record['Legal_Entity']} | Solution: {record['Solution']}")
                    with col_b:
                        if st.button(f"Select {record['Unique_ID']}", key=f"select_{record['Unique_ID']}"):
                            st.session_state.selected_record = record['Unique_ID']
                            st.success(f"Selected record {record['Unique_ID']}")
                            st.rerun()
        else:
            st.info("No records found. Create a new record to get started.")

def workflow_page():
    """Page for managing workflow steps"""
    if not st.session_state.selected_record:
        st.warning("Please select a record first from the Record Management page.")
        return
    
    wm = WorkflowManager()
    records, users, steps, workflow_status = wm.load_data()
    
    # Get record details
    record = records[records['Unique_ID'] == st.session_state.selected_record].iloc[0]
    
    st.markdown('<div class="main-header"><h1>🔄 Workflow Management</h1></div>', 
                unsafe_allow_html=True)
    
    # Record information
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="metric-card"><strong>Unique ID:</strong> {record["Unique_ID"]}</div>', 
                   unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><strong>Client Group:</strong> {record["Client_Group"]}</div>', 
                   unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card"><strong>Legal Entity:</strong> {record["Legal_Entity"]}</div>', 
                   unsafe_allow_html=True)
    
    st.markdown(f'<div class="metric-card"><strong>Solution:</strong> {record["Solution"]}</div>', 
               unsafe_allow_html=True)
    
    # Workflow steps
    st.subheader("Workflow Steps")
    
    current_workflow = workflow_status[workflow_status['Unique_ID'] == st.session_state.selected_record]
    
    # Group steps by header
    grouped_steps = {}
    for _, step in steps.iterrows():
        header = step['Header']
        if header not in grouped_steps:
            grouped_steps[header] = []
        grouped_steps[header].append(step)
    
    for header, header_steps in grouped_steps.items():
        st.markdown(f"### {header}")
        
        for step in header_steps:
            step_status = current_workflow[current_workflow['Step_ID'] == step['Step_ID']]
            
            if not step_status.empty:
                status = step_status.iloc[0]['Status']
                assigned_to = step_status.iloc[0]['Assigned_To']
                completed_by = step_status.iloc[0]['Completed_By']
                completed_date = step_status.iloc[0]['Completed_Date']
                comments = step_status.iloc[0]['Comments']
                
                # Determine step styling
                if status == 'Completed':
                    step_class = "step-completed"
                    status_icon = "✅"
                elif status == 'In Progress':
                    step_class = "workflow-step"
                    status_icon = "🔄"
                else:
                    step_class = "step-not-started"
                    status_icon = "⏳"
                
                st.markdown(f'''
                <div class="{step_class}">
                    <div class="step-header">{status_icon} Step {step['Step_ID']}: {step['Step_Name']}</div>
                    <div style="font-size: 0.9em; font-color: #000000; margin: 5px 0;">
                        <strong>Status:</strong> {status} | 
                        <strong>Required Role:</strong> <span class="role-badge role-{step['Required_Role'].lower()}">{step['Required_Role']}</span>
                        {f" | <strong>Assigned to:</strong> {assigned_to}" if assigned_to else ""}
                        {f" | <strong>Completed by:</strong> {completed_by} on {completed_date}" if completed_by else ""}
                    </div>
                </div>
                ''', unsafe_allow_html=True)
                
                # Step management controls
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                
                with col1:
                    new_assigned = st.selectbox(f"Assign to", 
                                              [""] + users['Username'].tolist(),
                                              key=f"assign_{step['Step_ID']}",
                                              index=users['Username'].tolist().index(assigned_to) + 1 if assigned_to in users['Username'].tolist() else 0)
                
                with col2:
                    new_status = st.selectbox(f"Status", 
                                            ["Not Started", "In Progress", "Completed"],
                                            key=f"status_{step['Step_ID']}",
                                            index=["Not Started", "In Progress", "Completed"].index(status))
                
                with col3:
                    # Check if current user can complete this step
                    can_complete = True
                    if step['Required_Role'] != 'Any' and st.session_state.current_user is not None:
                        user_role = st.session_state.current_user['Role']
                        required_role = step['Required_Role']
                        
                        if required_role == 'Manager' and user_role not in ['Manager', 'Lead']:
                            can_complete = False
                        elif required_role == 'Lead' and user_role != 'Lead':
                            can_complete = False
                    
                    if can_complete:
                        if st.button(f"Update", key=f"update_{step['Step_ID']}", use_container_width=True):
                            # Update workflow status
                            mask = (workflow_status['Unique_ID'] == st.session_state.selected_record) & \
                                   (workflow_status['Step_ID'] == step['Step_ID'])
                            
                            workflow_status.loc[mask, 'Status'] = new_status
                            workflow_status.loc[mask, 'Assigned_To'] = new_assigned
                            
                            if new_status == 'Completed' and st.session_state.current_user is not None:
                                workflow_status.loc[mask, 'Completed_By'] = st.session_state.current_user['Username']
                                workflow_status.loc[mask, 'Completed_Date'] = datetime.now()
                            
                            if wm.save_data(records, users, steps, workflow_status):
                                st.success(f"Step {step['Step_ID']} updated!")
                                st.rerun()
                    else:
                        st.warning(f"Only {step['Required_Role']} can complete")
                
                with col4:
                    # Comments button
                    if st.button(f"💬", key=f"comment_{step['Step_ID']}", help="Comments", use_container_width=True):
                        st.session_state[f"show_comments_{step['Step_ID']}"] = not st.session_state.get(f"show_comments_{step['Step_ID']}", False)
                
                # Comments section
                if st.session_state.get(f"show_comments_{step['Step_ID']}", False):
                    with st.expander(f"Comments for Step {step['Step_ID']}", expanded=True):
                        new_comment = st.text_area(f"Add your comments:", 
                                                 value=comments if pd.notna(comments) else "",
                                                 key=f"comment_text_{step['Step_ID']}",
                                                 height=100)
                        
                        if st.button(f"Save Comment", key=f"save_comment_{step['Step_ID']}", type="primary"):
                            mask = (workflow_status['Unique_ID'] == st.session_state.selected_record) & \
                                   (workflow_status['Step_ID'] == step['Step_ID'])
                            workflow_status.loc[mask, 'Comments'] = new_comment
                            
                            if wm.save_data(records, users, steps, workflow_status):
                                st.success("Comment saved!")
                                st.rerun()
                
                # File upload for steps requiring attachments
                if step['Attachment_Required']:
                    with st.expander(f"📎 Attachment Required for Step {step['Step_ID']}", expanded=False):
                        uploaded_file = st.file_uploader(f"Upload attachment", 
                                                       key=f"upload_{step['Step_ID']}")
                        if uploaded_file:
                            # In a real implementation, you'd save the file and store the path
                            st.info("File upload functionality would be implemented here")
                
                # Add some spacing between steps
                st.markdown("---")

def admin_page():
    """Admin page for user and workflow management"""
    if st.session_state.current_user is None or st.session_state.current_user['Role'] not in ['Lead', 'Manager']:
        st.error("Access denied. Only Lead and Manager roles can access admin functions.")
        return
    
    st.markdown('<div class="main-header"><h1>⚙️ Admin Console</h1></div>', 
                unsafe_allow_html=True)
    
    wm = WorkflowManager()
    records, users, steps, workflow_status = wm.load_data()
    
    tab1, tab2 = st.tabs(["User Management", "Workflow Configuration"])
    
    with tab1:
        st.header("User Management")
        
        # Display current users
        st.subheader("Current Users")
        edited_users = st.data_editor(users, use_container_width=True)
        
        if st.button("Save User Changes"):
            if wm.save_data(records, edited_users, steps, workflow_status):
                st.success("User data saved successfully!")
                st.rerun()
    
    with tab2:
        st.header("Workflow Step Configuration")
        
        st.info("Changes to workflow steps will only apply to new records created after the changes.")
        
        # Display current workflow steps
        edited_steps = st.data_editor(steps, use_container_width=True)
        
        if st.button("Save Workflow Changes"):
            if wm.save_data(records, users, edited_steps, workflow_status):
                st.success("Workflow configuration saved successfully!")
                st.rerun()

def main():
    """Main application function"""
    
    # User authentication
    user_info = user_authentication()
    if user_info is not None:
        st.session_state.current_user = user_info
    
    if st.session_state.current_user is None:
        st.warning("Please select a user to continue.")
        return
    
    # Navigation
    st.sidebar.header("📋 Navigation")
    
    pages = {
        "Record Management": record_management_page,
        "Workflow": workflow_page,
        "Admin Console": admin_page
    }
    
    # Show selected record in sidebar
    if st.session_state.selected_record:
        st.sidebar.success(f"Selected Record: {st.session_state.selected_record}")
        if st.sidebar.button("Clear Selection"):
            st.session_state.selected_record = None
            st.rerun()
    
    selected_page = st.sidebar.radio("Select Page", list(pages.keys()))
    
    # Run selected page
    pages[selected_page]()

if __name__ == "__main__":
    main()
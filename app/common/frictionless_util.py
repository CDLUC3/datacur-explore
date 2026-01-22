from frictionless import system, Resource, Detector
import pdb

# go through a naive auto-validation based on inferring the schema
def get_output(file_path):
    with system.use_context(trusted=True):
        # Define a custom schema with additional missing values
        detector = Detector(field_missing_values=["N/A", "NA", "None", "null", "nil"])
        resource = Resource(file_path, detector=detector)
        report = resource.validate()
        return make_readable_message(report)

def make_readable_message(report):
    if len(report.tasks) == 0 or len(report.tasks[0].errors) == 0:
        return ""
    error_types = {}

    # bucket into the same error types since the way it organizes data is annoying
    # for users to look at.  At least put errors under categories.
    for error in report.tasks[0].errors:
        if error.title not in error_types.keys():
            error_types[error.title] = []
        error_types[error.title].append(error.message)

    # Create markdown formatted string
    markdown_message = ""
    for error_type, messages in error_types.items():
        markdown_message += f"- {error_type}\n"
        for message in messages:
            markdown_message += f"  - {message}\n"

    return markdown_message

import numpy as np
import pandas as pd
import gradio as gr
from scipy.stats.mstats import winsorize
import matplotlib.pyplot as plt

# Helper function to create before and after box-whisker plots
def create_comparison_boxplot(df_original, df_winsorized, columns):
    fig, axes = plt.subplots(nrows=1, ncols=len(columns), figsize=(6 * len(columns), 5))
    if len(columns) == 1:
        axes = [axes]
    for ax, col in zip(axes, columns):
        ax.boxplot([df_original[col], df_winsorized[col]], labels=['Before', 'After'])
        ax.set_title(f'Box-Whisker Plot Comparison for {col}')
        ax.set_ylabel(col)
    plt.tight_layout()
    plot_filename = "comparison_boxplots.png"
    plt.savefig(plot_filename)
    plt.close(fig)
    return plot_filename

# Processing function with statistical comparison
def process_file(file, columns_to_winsorize, winsor_level):
    try:
        df = pd.read_csv(file.name)

        selected_columns = [col.strip() for col in columns_to_winsorize.split(',')]
        if all(var in df.columns for var in selected_columns):

            winsor_limits = [winsor_level / 100, winsor_level / 100]
            df_winsorized = df.copy()

            stats_summary = []

            for col in selected_columns:
                original_stats = {
                    "Variable": col,
                    "Type": "Before",
                    "Min": np.min(df[col]),
                    "Max": np.max(df[col]),
                    "Mean": np.mean(df[col]),
                }
                df_winsorized[col] = winsorize(df[col], limits=winsor_limits)
                winsorized_stats = {
                    "Variable": col,
                    "Type": "After",
                    "Min": np.min(df_winsorized[col]),
                    "Max": np.max(df_winsorized[col]),
                    "Mean": np.mean(df_winsorized[col]),
                }
                stats_summary.extend([original_stats, winsorized_stats])

            output_filename = "winsorized_dataset.csv"
            df_winsorized.to_csv(output_filename, index=False)

            plot_filename = create_comparison_boxplot(df, df_winsorized, selected_columns)

            #return output_filename, df_winsorized.head(), stats_summary, plot_filename
            stats_df = pd.DataFrame(stats_summary)
            return output_filename, df_winsorized.head(), stats_df, plot_filename

        else:
            return "Error: One or more specified variables do not exist in the dataset.", None, None, None
    except Exception as e:
        return str(e), None, None, None

# Listing columns function
def list_columns(file):
    try:
        df = pd.read_csv(file.name)
        return ', '.join(df.columns)
    except Exception as e:
        return str(e)

# Gradio Interface
winsor = gr.Blocks()
with winsor:
    gr.Markdown("## Winsorisation Tool with Comparative Box-Whisker Plot and Statistics")
    with gr.Row():
        file_input = gr.File(label="Upload CSV File")
        column_display = gr.Textbox(label="Column Names", interactive=False)
        list_button = gr.Button("List Columns")

    columns_input = gr.Textbox(label="Enter Columns to Winsorize (comma-separated)")
    winsor_level_input = gr.Number(label="Enter Winsorization Level (%)", value=5, precision=1)
    process_button = gr.Button("Process Data")

    output_file = gr.File(label="Download Processed Dataset")
    output_preview = gr.Dataframe(label="Preview of Processed Data")
    stats_output = gr.Dataframe(label="Statistics Before and After Winsorization")
    plot_output = gr.Image(label="Comparative Box-Whisker Plots")

    list_button.click(list_columns, inputs=[file_input], outputs=[column_display])
    process_button.click(
        process_file,
        inputs=[file_input, columns_input, winsor_level_input],
        outputs=[output_file, output_preview, stats_output, plot_output]
    )

winsor.launch()
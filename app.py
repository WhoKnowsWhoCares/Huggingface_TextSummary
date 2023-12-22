import gradio as gr

def greet(name):
    return "Hello " + name + "!"

demo = gr.Interface(
    fn=greet, 
    inputs=gr.Textbox(lines=5, placeholder="Write your text here..."), 
    outputs=gr.Textbox(lines=5, placeholder="Summary and Sentiment would be here..."), 
)
    
if __name__ == "__main__":
    demo.launch(show_api=False)   
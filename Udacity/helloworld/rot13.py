from utils import escape_html
import webapp2

rot13_form = """
Enter some text to ROT13:
<form method="post">
<textarea name="text">
%(text)s
</textarea>
<br>
<input type="submit">
</form>
"""



def rot13_encryption(text):
    normal_lower = "abcdefghijklmnopqrstuvwxyz"
    normal_upper = normal_lower.upper()
    rot13_lower = normal_lower[13:] + normal_lower[:13]
    rot13_upper = normal_upper[13:] + normal_upper[:13]
    text2 = ""
    for c in text:
        if c in normal_lower:
            text2 += rot13_lower[normal_lower.index(c)]
        elif c in normal_upper:
            text2 += rot13_upper[normal_upper.index(c)]
        else:
            text2 += c
    return text2
   
def write_form(requestHandler, form, dic):
    requestHandler.response.write(form % dic)
      
class ROT13(webapp2.RequestHandler):
        
    def get(self):
        write_form(self, rot13_form, {"text":""})
        
    def post(self):
        text = self.request.get("text")        
        text = rot13_encryption(text)
        write_form(self, rot13_form, {"text":escape_html(text)})
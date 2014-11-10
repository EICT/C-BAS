import jsonrpclib
import os.path
import tkMessageBox as box

from Tkinter import *
from registration_client_utils import  *

CONFIG_PATH = os.path.dirname(os.path.realpath(__file__)) + '/configuration/'
KEYS_PATH = os.path.dirname(os.path.realpath(__file__)) + '/keys/'

class RegistrationFrame(Frame):

    def __init__(self, parent):
        Frame.__init__(self, parent)


    # Registration Server Configuration Parameters
        self._registration_data = read_json_file(CONFIG_PATH + 'registration_app_config.json')
        self.server_ip = self._registration_data['registration_server']['ip_address']
        self.server_port = self._registration_data['registration_server']['port_number']

    # GUI related parameters
        self.parent = parent
        self.initUI()

    # Other utility parameters
        self.generate_keys = False

    def initUI(self):
        """
        Set up the Graphical User Interface
        """
        self.parent.title("Registration Application For CBAS")
        self.grid()

    #Labels & Areas
        self.first_name = Label(self, text="First Name:")
        self.first_name.grid(row=0, sticky = W)

        self.first_name_entry = Entry(self, width = 20)
        self.first_name_entry.grid(row=0, column = 1)

        self.last_name = Label(self, text="Last Name:")
        self.last_name.grid(row=1, sticky = W)
        self.last_name_entry = Entry(self, width = 20)
        self.last_name_entry.grid(row=1, column = 1)

        self.user_name = Label(self, text="User Name:")
        self.user_name.grid(row=2, sticky = W)
        self.user_name_entry = Entry(self, width = 20)
        self.user_name_entry.grid(row=2, column =1 )

        self.email = Label(self, text="Email:")
        self.email.grid(row = 3, sticky = W)
        self.email_entry = Entry(self, width = 20)
        self.email_entry.grid(row = 3 , column =1)


        self.radio_button_label = Label(self,
                                        text="""Choose Key Registration Method:""",
                                        justify = LEFT,
                                        padx = 20,
                                        pady = 10)
        self.radio_button_label.grid(row=4, sticky =W)

    #Radio Buttons
        v = IntVar()
        self.radio_button_generate= Radiobutton(self,
                                                text="Generate Keys",
                                                variable=v,
                                                value = 1,
                                                command = self.call_back('toggle', value=True))
        self.radio_button_generate.grid(row=5, column = 0)

        self.radio_button_provide = Radiobutton(self,
                                                text="Provide Keys",
                                                variable=v,
                                                value = 2,
                                                command = self.call_back('toggle', value = False))
        self.radio_button_provide.grid(row =5, column = 1)

    # Text Area
        self.public_key_label = Label(self, text="Public SSH Key:")
        self.public_key_label.grid(row=6, column=0,  sticky = W)
        self.public_key_text_area = Text(self, height=2, width=100)
        self.public_key_text_area.grid( row = 6, columnspan = 1, column = 1, sticky = W+E)

        self.private_key_label = Label(self, text="Private SSH Key:")
        self.private_key_label.grid(row=7, column=0,  sticky = W)
        self.private_key_text_area = Text(self, height=2, width=100)
        self.private_key_text_area.grid( row = 7, columnspan = 1, column = 1, sticky = W+E)

        self.user_certificate = Label(self, text="User Certificate:")
        self.user_certificate.grid(row=8, column=0,  sticky = W)
        self.user_certificate = Text(self, height=2, width=100)
        self.user_certificate.grid( row = 8, columnspan = 1, column = 1, sticky = W+E)

        self.user_certificate_key = Label(self, text="User Certificate Key:")
        self.user_certificate_key.grid(row=9, column=0,  sticky = W)
        self.user_certificate_key = Text(self, height=2, width=100)
        self.user_certificate_key.grid( row = 9, columnspan = 1, column = 1, sticky = W+E)

    #Buttons
        self.button_register= Button(self, text="Register",
                                     command=self.call_back('register'))
        self.button_register.grid(row=10, column = 0)

        self.button_quit = Button(self, text="Quit", command=quit)
        self.button_quit.grid(row=10, column = 1)

        self.button_clear = Button(self, text="Clear", command=self.call_back('clear'))
        self.button_clear.grid(row=10, column = 2)


    def call_back (self, function, **kwargs):
        """
        A call back function for button events

        Args:
            function: the event / function name to generate on call back
            kwargs: to pass other values to the function

        Return:
            return the result of the event generated
        """
        server = jsonrpclib.Server('http://%s:%s' % (self.server_ip, self.server_port))
        def register():
            first_name = self.first_name_entry.get()
            last_name = self.last_name_entry.get()
            user_name =  self.user_name_entry.get()
            email = self.email_entry.get()
            if not self.generate_keys:

                public_key_value = self.public_key_text_area.get('0.0', END)
                if first_name and last_name and user_name and email and public_key_value :

                    member, key = server.register_user(self.first_name_entry.get(),
                                                           self.last_name_entry.get(),
                                                           self.user_name_entry.get(),
                                                           self.email_entry.get(),
                                                           self.public_key_text_area.get('0.0', END))


                    certificate_value = member['MEMBER_CERTIFICATE'] if member else "ERROR"
                    self.user_certificate.insert(END, certificate_value)
                    certificate_key_value = member['MEMBER_CERTIFICATE_KEY'] if member else "ERROR"
                    self.user_certificate_key.insert(END, certificate_key_value)
                    self.raise_tkinter_message('registered')() if member else self.raise_tkinter_message('fail')()
                else:
                    self.raise_tkinter_message('missing')()
            else:
                if first_name and last_name and user_name and email:
                    public_key_value, private_key_value = get_ssh_keys(self.first_name_entry.get(),
                                                    self.last_name_entry.get(),
                                                    KEYS_PATH)

                    self.public_key_text_area.insert(END, public_key_value)
                    self.private_key_text_area.insert(END, private_key_value)
                    member, key = server.register_user(self.first_name_entry.get(),
                                                       self.last_name_entry.get(),
                                                       self.user_name_entry.get(),
                                                       self.email_entry.get(),
                                                       public_key_value)

                    certificate_value = member['MEMBER_CERTIFICATE'] if member else "ERROR"
                    self.user_certificate.insert(END, certificate_value)
                    certificate_key_value = member['MEMBER_CERTIFICATE_KEY'] if member else "ERROR"
                    self.user_certificate_key.insert(END, certificate_key_value)
                    self.raise_tkinter_message('registered')() if member else self.raise_tkinter_message('fail')()
                else:
                    self.raise_tkinter_message('missing')()

        def toggle_generate_key():
            self.generate_keys = kwargs['value']

        def clear_text():
            self.public_key_text_area.delete('1.0', END)
            self.private_key_text_area.delete('1.0', END)
            self.user_certificate.delete('1.0', END)
            self.user_certificate_key.delete('1.0', END)
            self.user_name_entry.delete(0, END)
            self.email_entry.delete(0, END)
            self.first_name_entry.delete(0, END)
            self.last_name_entry.delete(0, END)


        #Add call back functions here
        functions = {'register': register,
                     'toggle': toggle_generate_key,
                     'clear': clear_text}

        if function in functions: return functions[function]
        else: return None


    def raise_tkinter_message(self,function):
        """
        A call back function for errors are notifications

        Args:
            function: the error / notification name to generate on call back
            kwargs: to pass other values to the function

        Return:
            return the result of the error / notification generated
        """
        def missing_value():
            box.showerror('Missing Entry', 'Can not perform operation,'
                                           ' please make sure to fill all the registration entries!')

        def registration_success():
            box.showinfo('Registration Success', 'Registration was successful,'
                                                 ' please copy your key from the text area!')

        def registration_failure():
            box.showerror('Registration Failure', 'Server Could not register the user,'
                                           ' please make sure to fill all the registration entries!')

        functions = {'missing': missing_value,
                     'registered': registration_success,
                     'fail':registration_failure}

        if function in functions: return functions[function]
        else: return None


def main():
    """
    Run the Application
    """
    root = Tk()
    RegistrationFrame(root)
    root.mainloop()

    # server = jsonrpclib.Server('http://localhost:1234')
    # result =  server.register_user('adel', 'zalok', 'alice', 'alice@example.com' )
    # print result

if __name__=="__main__":
    main()

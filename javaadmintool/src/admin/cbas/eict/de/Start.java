package admin.cbas.eict.de;
import java.awt.BorderLayout;
import java.util.prefs.*;
import java.awt.Color;
import java.awt.Dimension;
import java.awt.FlowLayout;
import java.awt.Toolkit;
import javax.swing.JButton;
import javax.swing.JDialog;
import javax.swing.JFileChooser;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.SwingConstants;
import javax.swing.border.EmptyBorder;
import javax.swing.JLabel;
import javax.swing.JTextField;
import java.awt.GridLayout;
import javax.swing.BoxLayout;
import java.awt.event.ActionListener;
import java.awt.event.ActionEvent;
import java.io.File;
import javax.swing.border.BevelBorder;

public class Start extends JDialog {

	/**
	 * 
	 */
	private static final long serialVersionUID = -7378200580272158884L;
	private final JPanel contentPanel = new JPanel();
	private JTextField textFieldIP;
	private JTextField textFieldPort;
	private JTextField textFieldCert;
	private JTextField textFieldKey;
	static File certFile, certKeyFile; 
	static String host;
	static int port;
	static Object credentials[];	
	JLabel status;
	private Preferences prefs;
	/**
	 * Launch the application.
	 */
	public static void main(String[] args) {
		try {
			new Start();
		} catch (Exception e) {
			e.printStackTrace();
		}
	}

	/**
	 * Create the dialog.
	 */
	public Start() {
		this.setTitle("C-BAS Admin Tool");		
		getContentPane().setLayout(new BorderLayout());
		contentPanel.setBorder(new EmptyBorder(5, 5, 5, 5));
		getContentPane().add(contentPanel, BorderLayout.CENTER);
		contentPanel.setLayout(new GridLayout(8, 1, 0, 0));
		prefs = Preferences.userNodeForPackage(this.getClass());
		
		JLabel lblCbasHostIp = new JLabel("C-BAS Host Name/IP Address:");
		contentPanel.add(lblCbasHostIp);
		
		textFieldIP = new JTextField();
		textFieldIP.setText(prefs.get("host","127.0.0.1"));
		contentPanel.add(textFieldIP);
		textFieldIP.setColumns(10);
		
		JLabel lblCbasHostPort = new JLabel("C-BAS Host Port:");
		contentPanel.add(lblCbasHostPort);
		
		textFieldPort = new JTextField();
		textFieldPort.setText(prefs.get("port", "8008"));
		contentPanel.add(textFieldPort);
		textFieldPort.setColumns(10);
		
		JLabel lblRootMemberCertificate = new JLabel("Root Member Certificate:");
		contentPanel.add(lblRootMemberCertificate);
		
		JPanel panel = new JPanel();
		contentPanel.add(panel);
		panel.setLayout(new BorderLayout(0, 0));			
		textFieldCert = new JTextField();
		textFieldCert.setEditable(false);
		panel.add(textFieldCert, BorderLayout.CENTER);
		textFieldCert.setColumns(10);
		JButton btnBrowseCert = new JButton("...");
		final JFileChooser fileChooser = new JFileChooser(); 
		fileChooser.setFileSelectionMode(JFileChooser.FILES_ONLY);
		btnBrowseCert.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent arg0) {
				
				int result = fileChooser.showOpenDialog(Start.this);

				if (result == JFileChooser.APPROVE_OPTION) {
				    certFile = fileChooser.getSelectedFile();
				    textFieldCert.setText(certFile.getPath());	
				    String expectedKeyFileName = certFile.getName().replace("-cert", "-key");
				    File expectedKeyFilePath = new File(certFile.getParent(), expectedKeyFileName);
				    if(expectedKeyFileName.endsWith(".pem") && expectedKeyFilePath.exists())
				    {
				    	certKeyFile = expectedKeyFilePath;
				    	textFieldKey.setText(certKeyFile.getPath());
				    }
				}
			}
		});
		panel.add(btnBrowseCert, BorderLayout.EAST);
		String savedCertFileName = prefs.get("cert_file", null);
		if(savedCertFileName != null && new File(savedCertFileName).exists())
		{
			certFile = new File(savedCertFileName);
			textFieldCert.setText(certFile.getPath());
		}
		
		JLabel lblRootMemberCertificate_1 = new JLabel("Root Member Certificate Key:");
		contentPanel.add(lblRootMemberCertificate_1);
		JPanel panel2 = new JPanel();
		contentPanel.add(panel2);
		panel2.setLayout(new BorderLayout(0, 0));
		textFieldKey = new JTextField();
		textFieldKey.setEditable(false);
		panel2.add(textFieldKey, BorderLayout.CENTER);
		textFieldKey.setColumns(10);
		JButton btnBrowseKey = new JButton("...");
		panel2.add(btnBrowseKey, BorderLayout.EAST);
		btnBrowseKey.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent arg0) {

				int result = fileChooser.showOpenDialog(Start.this);
				if (result == JFileChooser.APPROVE_OPTION) {
				    certKeyFile = fileChooser.getSelectedFile();
				    textFieldKey.setText(certKeyFile.getPath());
				}
			}
		});
		String savedKeyFileName = prefs.get("key_file", null);
		if(savedKeyFileName != null && new File(savedKeyFileName).exists())
		{
			certKeyFile = new File(savedKeyFileName);
			textFieldKey.setText(certKeyFile.getPath());
		}

		
		JPanel buttomPane = new JPanel();
		getContentPane().add(buttomPane, BorderLayout.SOUTH);
		buttomPane.setLayout(new BorderLayout(0, 0));
		
		JPanel buttonPanel = new JPanel();
		FlowLayout fl_buttonPanel = (FlowLayout) buttonPanel.getLayout();
		fl_buttonPanel.setAlignment(FlowLayout.RIGHT);
		buttomPane.add(buttonPanel);
		JButton okButton = new JButton("Connect");
		buttonPanel.add(okButton);
		okButton.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent arg0) {
				
				//For the moment valdation is bypassed
				host = textFieldIP.getText();
				
				//Validate Port number
				try
				{
					port = Integer.parseInt(textFieldPort.getText().trim());
					textFieldPort.setBackground(Color.white);
				}catch(NumberFormatException ex)
				{
					textFieldPort.setBackground(Color.pink);
					return;
				}
						
				//Validate Cert file
				if(textFieldCert.getText().trim().length()==0){
					textFieldCert.setBackground(Color.pink);
					return;
				}else
					textFieldCert.setBackground(Color.white);
				
				//Validate Key file
				if(textFieldKey.getText().trim().length()==0){
					textFieldKey.setBackground(Color.pink);
					return;
				}else
					textFieldKey.setBackground(Color.white);
				
				//Save given config inputs
				prefs.put("key_file", certKeyFile.getPath());
				prefs.put("cert_file", certFile.getPath());
				prefs.put("host", textFieldIP.getText());
				prefs.put("port", textFieldPort.getText());
				try {
					prefs.flush();
				} catch (BackingStoreException e) {}
				
				//Try connecting and loading data
				
				connectAndLoad();
				
			}
		});
		okButton.setActionCommand("OK");
		getRootPane().setDefaultButton(okButton);
		
		JPanel statusPanel = new JPanel();
		statusPanel.setBorder(new BevelBorder(BevelBorder.LOWERED));
		statusPanel.setPreferredSize(new Dimension(this.getWidth(), 18));
		statusPanel.setLayout(new BoxLayout(statusPanel, BoxLayout.X_AXIS));
		buttomPane.add(statusPanel, BorderLayout.SOUTH);
		
		status = new JLabel("Ready");
		status.setHorizontalAlignment(SwingConstants.LEFT);
		statusPanel.add(status);
		
		setDefaultCloseOperation(JDialog.DISPOSE_ON_CLOSE);
		setSize(450,300);
		Dimension dim = Toolkit.getDefaultToolkit().getScreenSize();
		this.setLocation(dim.width/2-this.getSize().width/2, dim.height/2-this.getSize().height/2);		
		setVisible(true);		
	}
	
	private void connectAndLoad()
	{
		Runnable thread = new Runnable(){

			@Override
			public void run() {

				//Set endpoints
				MemberAuthorityAPI.setHostAndPort(host, port);
				SliceAuthorityAPI.setHostAndPort(host, port);
				
				//Try connecting with C-BAS
				status.setText("Trying to connect...");
				try {
					FAPIClient.init(certFile, certKeyFile);
				} catch (Exception ex) {
					
					String userFriendlyMessage = ex.getMessage();
					if(ex.getMessage().contains("invalid"))
						userFriendlyMessage = "Certificate or key file contents are unexpected.<br/> <br/> ("+ex.getMessage()+")";
					
					JOptionPane.showMessageDialog(
						    Start.this, "<html><body><p style='width: 300px;'>"+userFriendlyMessage+"</p></body></html>", 
						    "Error", JOptionPane.ERROR_MESSAGE);	
					
					status.setText("Ready");
					return;
				}			
				
				//Fetch Credentials
				status.setText("Fetching member credentials...");
				
				String mem_urn = Utils.extractOwnerURN(certFile);
				credentials = MemberAuthorityAPI.getCredential(mem_urn);
				if(credentials == null)
				{
					JOptionPane.showMessageDialog( Start.this, 
						    "<html><body><p style='width: 300px;'>"+MemberAuthorityAPI.output+"</p></body></html>", 
						    "Error", JOptionPane.ERROR_MESSAGE);
					status.setText("Ready");
					return;					
				}
				MemberAuthorityAPI.credentials = credentials;
				SliceAuthorityAPI.credentials = credentials;
				
				
				//Load Users data
				status.setText("Loading members' data...");
				Members.memberDetails = MemberAuthorityAPI.lookupAll();
				if(Members.memberDetails == null)
				{
					JOptionPane.showMessageDialog( Start.this, 
						    "<html><body><p style='width: 300px;'>"+MemberAuthorityAPI.output+"</p></body></html>", 
						    "Error", JOptionPane.ERROR_MESSAGE);
					status.setText("Ready");
					return;					
				}
				MemberAuthorityAPI.fetchCRL();
				if(MemberAuthorityAPI.crl == null)
				{
					JOptionPane.showMessageDialog( Start.this, 
						    "<html><body><p style='width: 300px;'>"+MemberAuthorityAPI.output+"</p></body></html>", 
						    "Error", JOptionPane.ERROR_MESSAGE);
					status.setText("Ready");
					return;					
				}
				
				//Load project data
				status.setText("Loading projects' data...");
				Projects.projectDetailsList = SliceAuthorityAPI.lookupAllProjects();
				if(Projects.projectDetailsList == null)
				{
					JOptionPane.showMessageDialog( Start.this, 
						    "<html><body><p style='width: 300px;'>"+SliceAuthorityAPI.output+"</p></body></html>", 
						    "Error", JOptionPane.ERROR_MESSAGE);
					status.setText("Ready");
					return;					
				}

				//Load slice data
				status.setText("Loading slices' data...");
				Slices.sliceDetailsList = SliceAuthorityAPI.lookupAllSlices();
				if(Slices.sliceDetailsList == null)
				{
					JOptionPane.showMessageDialog( Start.this, 
						    "<html><body><p style='width: 300px;'>"+SliceAuthorityAPI.output+"</p></body></html>", 
						    "Error", JOptionPane.ERROR_MESSAGE);
					status.setText("Ready");
					return;					
				}

				status.setText("Initializing GUI...");
				MainGUI mainGUI = new MainGUI();
				
				//Dispose dialog and show main GUI
				Start.this.dispose();
				mainGUI.setVisible(true);
				
			}
			
		};
		
		(new Thread(thread)).start();
	}
}

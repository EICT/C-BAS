package admin.cbas.eict.de;

import java.awt.Color;
import java.awt.Desktop;
import java.awt.Dimension;
import java.awt.Font;
import java.awt.Toolkit;

import javax.imageio.ImageIO;
import javax.swing.JFrame;
import javax.swing.JTabbedPane;

import java.awt.BorderLayout;

import javax.swing.ImageIcon;
import javax.swing.JDialog;
import javax.swing.JEditorPane;
import javax.swing.JLabel;
import javax.swing.JOptionPane;
import javax.swing.JMenuBar;
import javax.swing.JMenu;
import javax.swing.JMenuItem;
import javax.swing.KeyStroke;
import javax.swing.UIDefaults;
import javax.swing.border.EmptyBorder;
import javax.swing.event.HyperlinkEvent;
import javax.swing.event.HyperlinkListener;

import admin.cbas.eict.de.LoggingAuthorityAPI.LogEvent;
import admin.cbas.eict.de.MemberAuthorityAPI.Member;
import admin.cbas.eict.de.SliceAuthorityAPI.Project;
import admin.cbas.eict.de.SliceAuthorityAPI.Slice;

import java.awt.event.KeyEvent;
import java.awt.event.InputEvent;
import java.awt.event.ActionListener;
import java.awt.event.ActionEvent;
import java.io.File;
import java.net.URI;

public class MainGUI {

	private JFrame frame;
	Members panelUsers;
	Slices panelSlices; 
	Projects panelProjects;
	Logs  panelLog;
	JTabbedPane tabbedPane;
	static final int MEMBERS_TAB_INDEX=0, PROJECTS_TAB_INDEX=1, SLICES_TAB_INDEX=2;


	/**
	 * Create the application.
	 */
	public MainGUI(Member[] memberSet, Project[] projectSet, Slice[] sliceSet, LogEvent[] logs) {

		frame = new JFrame();
		frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		frame.setTitle("C-BAS Admin Tool");

		
		tabbedPane = new JTabbedPane(JTabbedPane.TOP);
		frame.getContentPane().add(tabbedPane, BorderLayout.CENTER);
		
		panelUsers = new Members(this, memberSet);
		tabbedPane.addTab("Members", null, panelUsers, "Manage members");
		
		
		panelProjects = new Projects(this, projectSet);
		tabbedPane.addTab("Projects", null, panelProjects, "Manage projects");
		
		panelSlices = new Slices(this, sliceSet);
		tabbedPane.addTab("Slices", null, panelSlices, "Manage slices");

		panelLog = new Logs(this, logs);
		tabbedPane.addTab("Logs", null, panelLog, "View event logs");
		
		JMenuBar menuBar = new JMenuBar();
		frame.setJMenuBar(menuBar);
		
		JMenu mnFile = new JMenu("File");
		menuBar.add(mnFile);
		
		JMenuItem mntmExit = new JMenuItem("Exit");
		mntmExit.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent arg0) {
				System.exit(0);
			}
		});
		
		JMenuItem mntmAbout = new JMenuItem("About");
		mntmAbout.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent arg0) {
				showAboutDialog();
			}
		});
		mnFile.add(mntmAbout);
		mntmExit.setAccelerator(KeyStroke.getKeyStroke(KeyEvent.VK_X, InputEvent.CTRL_MASK | InputEvent.SHIFT_MASK));
		mnFile.add(mntmExit);
		
		JMenu mnRefresh = new JMenu("Refresh");
		menuBar.add(mnRefresh);
		
		JMenuItem mntmLogs = new JMenuItem("Logs only");
		mntmLogs.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent arg0) {
				
			}
		});
		//mnRefresh.add(mntmLogs);
		
		JMenuItem mntmAll = new JMenuItem("All data");
		mntmAll.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent arg0) {
				JDialog dialog = new JDialog(frame, "Refresh", true);
				dialog.getContentPane().setLayout(new BorderLayout(5,5));
				//dialog.setDefaultCloseOperation(JDialog.DO_NOTHING_ON_CLOSE);
				JLabel status = new JLabel("Initiating process...");
				status.setBorder(new EmptyBorder(0, 10, 0, 0));
				dialog.getContentPane().add(status, BorderLayout.CENTER);
				dialog.setAlwaysOnTop(true);
				dialog.setSize(300, 100);
				dialog.setLocationRelativeTo(frame);
				Start.connectAndLoad(status, false);
				dialog.setVisible(true);
			}
		});
		mnRefresh.add(mntmAll);
		
		frame.pack();
		Dimension dim = Toolkit.getDefaultToolkit().getScreenSize();
		frame.setLocation(dim.width/2-frame.getSize().width/2, dim.height/2-frame.getSize().height/2);

		//set icon image
		try{
			 
			File iconFile = new File("icon.png");
			
			if(iconFile.exists())
				frame.setIconImage(ImageIO.read(iconFile));
			else
				frame.setIconImage(new ImageIcon(getClass().getResource("icon.png")).getImage());
		}catch(Exception ex){}
		
	}
	
	public void setVisible(boolean f)
	{
		frame.setVisible(f);
	}
	
	public void setSelectedProject(String projectName)
	{
		Object[] allProjects = getProjectsArray();
		for(int i=0; i<allProjects.length; i++)
			if(((Project)allProjects[i]).name.equals(projectName) )
			{
				panelProjects.projectList.setSelectedValue(allProjects[i], true);
				break;
			}		

		this.tabbedPane.setSelectedIndex(PROJECTS_TAB_INDEX);
		
	}
	public void setSelectedSlice(String sliceName)
	{
		Object[] allSlices = getSlicesArray();
		for(int i=0; i<allSlices.length; i++)
			if(((Slice)allSlices[i]).name.equals(sliceName) )
			{
				panelSlices.sliceList.setSelectedValue(allSlices[i], true);
				break;
			}
		this.tabbedPane.setSelectedIndex(SLICES_TAB_INDEX);
				
	}
	public void setSelectedMember(String username)
	{
		Object[] allMembers = getMembersArray();
		for(int i=0; i<allMembers.length; i++)
			if(((Member)allMembers[i]).username.equals(username) )
			{
				panelUsers.userList.setSelectedValue(allMembers[i], true);
				break;
			}
		this.tabbedPane.setSelectedIndex(MEMBERS_TAB_INDEX);
	}
	
	public Object[] getMembersArray()
	{
		return panelUsers.getMemberArray();
	}

	public Object[] getSlicesArray()
	{
		return panelSlices.getSliceArray();
	}

	public Object[] getProjectsArray()
	{
		return panelProjects.getProjectArray();
	}
	
	private void showAboutDialog()
	{
	    JLabel label = new JLabel();
	    Font font = label.getFont();

	    StringBuffer style = new StringBuffer("font-family:" + font.getFamily() + ";");
	    style.append("font-weight:" + (font.isBold() ? "bold" : "normal") + ";");
	    style.append("font-size:" + font.getSize() + "pt;");

	    JEditorPane ep = new JEditorPane("text/html", "<html><body style=\"" + style + "\">" //
	            + "Admin tool for <a href=\"http://eict.de/c-bas\">C-BAS</a><br/>Version: 1.0<br/><a href=\"https://github.com/EICT/C-BAS/blob/master/LICENCE.txt\">License</a><br/><br/>Developed by <a href=\"http://www.eict.de\">EICT GmbH</a>, Berlin, Germany" //
	            + "</body></html>");

	    ep.addHyperlinkListener(new HyperlinkListener()
	    {
	        @Override
	        public void hyperlinkUpdate(HyperlinkEvent e)
	        {
	            if (e.getEventType().equals(HyperlinkEvent.EventType.ACTIVATED))
	            {
	                if (Desktop.isDesktopSupported()) {
	                    try {
	                      Desktop.getDesktop().browse(URI.create(e.getURL().toString()));
	                    } catch (Exception ex) {}
	                }
	            }
	        }
	    });
	    ep.setEditable(false);
	    Color bgColor = frame.getBackground();
	    UIDefaults defaults = new UIDefaults();
	    defaults.put("EditorPane[Enabled].backgroundPainter", bgColor);
	    ep.putClientProperty("Nimbus.Overrides", defaults);
	    ep.putClientProperty("Nimbus.Overrides.InheritDefaults", true);
	    ep.setBackground(bgColor);	    

	    // show
	    JOptionPane.showMessageDialog(frame, ep, "About", JOptionPane.INFORMATION_MESSAGE);		
	}

	public void refresh(Member[] memberSet, Project[] projectSet,
			Slice[] sliceSet, LogEvent[] logs) {
		
		panelUsers.refresh(memberSet);
		panelProjects.refresh(projectSet);
		panelSlices.refresh(sliceSet);
		panelLog.refresh(logs);		
	}

}

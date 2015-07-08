package admin.cbas.eict.de;

import java.awt.Dimension;
import java.awt.Toolkit;

import javax.swing.JFrame;
import javax.swing.JTabbedPane;

import java.awt.BorderLayout;

import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.JMenuBar;
import javax.swing.JMenu;
import javax.swing.JMenuItem;
import javax.swing.KeyStroke;

import admin.cbas.eict.de.MemberAuthorityAPI.Member;
import admin.cbas.eict.de.SliceAuthorityAPI.Project;
import admin.cbas.eict.de.SliceAuthorityAPI.Slice;

import java.awt.event.KeyEvent;
import java.awt.event.InputEvent;
import java.awt.event.ActionListener;
import java.awt.event.ActionEvent;

public class MainGUI {

	private JFrame frame;
	Members panelUsers;
	Slices panelSlices; 
	Projects panelProjects;
	JPanel panelLog;
	JTabbedPane tabbedPane;
	static final int MEMBERS_TAB_INDEX=0, PROJECTS_TAB_INDEX=1, SLICES_TAB_INDEX=2;


	/**
	 * Create the application.
	 */
	public MainGUI(Member[] memberSet, Project[] projectSet, Slice[] sliceSet) {

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

		JPanel panelLog = new Logs();
		tabbedPane.addTab("Logs", null, panelLog, null);
		
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
				JOptionPane.showMessageDialog(frame, "<html>Admin tool for <a href=\"http://eict.de/c-bas\">C-BAS</a><br/>Version: beta 1<br/><br/>Developed by <a href=\"http://www.eict.de\">EICT GmbH</>, Berlin", "About", JOptionPane.INFORMATION_MESSAGE);
			}
		});
		mnFile.add(mntmAbout);
		mntmExit.setAccelerator(KeyStroke.getKeyStroke(KeyEvent.VK_X, InputEvent.CTRL_MASK | InputEvent.SHIFT_MASK));
		mnFile.add(mntmExit);
		
		frame.pack();
		Dimension dim = Toolkit.getDefaultToolkit().getScreenSize();
		frame.setLocation(dim.width/2-frame.getSize().width/2, dim.height/2-frame.getSize().height/2);						
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

}

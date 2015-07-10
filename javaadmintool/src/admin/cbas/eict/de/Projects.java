package admin.cbas.eict.de;

import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.Dimension;

import javax.swing.JList;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.ListSelectionModel;
import javax.swing.border.TitledBorder;
import javax.swing.event.ListSelectionEvent;
import javax.swing.event.ListSelectionListener;
import javax.swing.text.AbstractDocument;
import javax.swing.JSplitPane;
import javax.swing.JTable;
import javax.swing.JButton;

import java.awt.GridBagLayout;

import javax.swing.JLabel;

import java.awt.GridBagConstraints;

import javax.swing.JTextField;

import java.awt.Insets;
import java.util.HashSet;
import java.util.LinkedList;

import javax.swing.JTextArea;

import admin.cbas.eict.de.MemberAuthorityAPI.Member;
import admin.cbas.eict.de.SliceAuthorityAPI.Membership;
import admin.cbas.eict.de.SliceAuthorityAPI.Project;
import admin.cbas.eict.de.SliceAuthorityAPI.Slice;

import java.awt.event.ActionListener;
import java.awt.event.ActionEvent;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;

public class Projects extends JPanel {

	/**
	 * 
	 */
	private static final long serialVersionUID = 4216474279890435844L;
	JList projectList, projectSliceList;
	SortedListModel<Project> projectListModel;
	SortedListModel<String> projectSliceListModel;
	private JTable memberTable;
	private JTextField textFieldProjectURN;
	private JTextField textFieldExpiry;
	private JTextArea textAreaDesc;
	CustomTableModel tableModel;
//	static LinkedList<SliceAuthorityAPI.Project> projectDetailsList;
	private JTextField textFieldCreation;
	MainGUI mainGUI;
	

	/**
	 * Create the frame.
	 */
	public Projects(MainGUI parent, Project[] projectData) {
		
		mainGUI = parent;
		setLayout(new BorderLayout(0, 0));
				
		JScrollPane scrollPane = new JScrollPane();		
		
		projectListModel = new SortedListModel<Project>();
		if(projectData != null)
			projectListModel.addAll(projectData);
		
		projectList = new JList(projectListModel);
		projectList.setSelectionMode(ListSelectionModel.SINGLE_SELECTION);
		scrollPane.setViewportView(projectList);
		TitledBorder titled = new TitledBorder("List of Projects");
		scrollPane.setBorder(titled);
		scrollPane.setPreferredSize(new Dimension(300,400));
		
				
		JPanel rightPanel = new JPanel();
		rightPanel.setLayout(new BorderLayout(0, 0));
		
		JPanel panelInfo = new JPanel();
		rightPanel.add(panelInfo, BorderLayout.NORTH);
		GridBagLayout gbl_panelInfo = new GridBagLayout();
		panelInfo.setLayout(gbl_panelInfo);
		
		
		JLabel lblNewLabel = new JLabel("URN:");
		GridBagConstraints gbc_lblNewLabel = new GridBagConstraints();
		gbc_lblNewLabel.insets = new Insets(10, 0, 5, 5);
		gbc_lblNewLabel.weightx = 0.01;
		gbc_lblNewLabel.anchor = GridBagConstraints.EAST;
		gbc_lblNewLabel.gridx = 0;
		gbc_lblNewLabel.gridy = 0;
		panelInfo.add(lblNewLabel, gbc_lblNewLabel);
		
		textFieldProjectURN = new JTextField();
		textFieldProjectURN.setEditable(false);
		GridBagConstraints gbc_textFieldProjectURN = new GridBagConstraints();
		gbc_textFieldProjectURN.insets = new Insets(10, 0, 5, 0);
		
		gbc_textFieldProjectURN.weightx = 0.99;
		gbc_textFieldProjectURN.fill = GridBagConstraints.HORIZONTAL;
		gbc_textFieldProjectURN.gridx = 1;
		gbc_textFieldProjectURN.gridy = 0;
		panelInfo.add(textFieldProjectURN, gbc_textFieldProjectURN);
		
		
		JLabel lblNewLabel_1 = new JLabel("Expiration:");
		GridBagConstraints gbc_lblNewLabel_1 = new GridBagConstraints();
		gbc_lblNewLabel_1.insets = new Insets(10, 0, 5, 5);
		gbc_lblNewLabel_1.weightx = 0.01;
		gbc_lblNewLabel_1.anchor = GridBagConstraints.EAST;
		
		gbc_lblNewLabel_1.gridx = 0;
		gbc_lblNewLabel_1.gridy = 2;
		panelInfo.add(lblNewLabel_1, gbc_lblNewLabel_1);
		
		textFieldExpiry = new JTextField();
		textFieldExpiry.setEditable(false);
		GridBagConstraints gbc_textFieldExpiry = new GridBagConstraints();
		gbc_textFieldExpiry.insets = new Insets(10, 0, 5, 0);
		gbc_textFieldExpiry.weightx = 0.99;
		gbc_textFieldExpiry.fill = GridBagConstraints.HORIZONTAL;
		gbc_textFieldExpiry.gridx = 1;
		gbc_textFieldExpiry.gridy = 2;
		panelInfo.add(textFieldExpiry, gbc_textFieldExpiry);
		
		JLabel lblSliceDescription = new JLabel("Description:");
		GridBagConstraints gbc_lblSliceDescription = new GridBagConstraints();
		gbc_lblSliceDescription.insets = new Insets(10, 0, 20, 5);
		gbc_lblSliceDescription.gridx = 0;
		gbc_lblSliceDescription.gridy = 3;
		panelInfo.add(lblSliceDescription, gbc_lblSliceDescription);
		
		textAreaDesc = new JTextArea();
		textAreaDesc.setEditable(false);
		GridBagConstraints gbc_textArea = new GridBagConstraints();
		gbc_textArea.fill = GridBagConstraints.BOTH;
		gbc_textArea.insets = new Insets(10, 0, 20, 0);
		gbc_textArea.gridx = 1;
		gbc_textArea.gridy = 3;
		gbc_textArea.ipady = 30;
		panelInfo.add(new JScrollPane(textAreaDesc), gbc_textArea);
		
		JLabel lblCreation = new JLabel("Creation:");
		GridBagConstraints gbc_lblCreation = new GridBagConstraints();
		gbc_lblCreation.anchor = GridBagConstraints.EAST;
		gbc_lblCreation.insets = new Insets(10, 0, 0, 5);
		gbc_lblCreation.gridx = 0;
		gbc_lblCreation.gridy = 1;
		panelInfo.add(lblCreation, gbc_lblCreation);
		
		textFieldCreation = new JTextField();		
		textFieldCreation.setEditable(false);
		GridBagConstraints gbc_textFieldCreation = new GridBagConstraints();
		gbc_textFieldCreation.insets = new Insets(10, 0, 5, 0);
		gbc_textFieldCreation.weightx = 0.99;
		gbc_textFieldCreation.fill = GridBagConstraints.HORIZONTAL;
		gbc_textFieldCreation.gridx = 1;
		gbc_textFieldCreation.gridy = 1;
		panelInfo.add(textFieldCreation, gbc_textFieldCreation);
		
		
		tableModel = new CustomTableModel(null, new String[]{"Member", "Role"});
		
		JSplitPane splitPane_right = new JSplitPane();
		splitPane_right.setOrientation(JSplitPane.VERTICAL_SPLIT);		
		rightPanel.add(splitPane_right, BorderLayout.CENTER);
		
		memberTable = new JTable(tableModel);
		memberTable.setAutoCreateRowSorter(true);
		memberTable.setSelectionMode(ListSelectionModel.SINGLE_SELECTION);
		memberTable.getColumnModel().getColumn(0).setPreferredWidth(300);
		memberTable.getColumnModel().getColumn(1).setPreferredWidth(75);
		memberTable.getColumnModel().getColumn(1).setMaxWidth(75);
		JScrollPane spMemberTable = new JScrollPane(memberTable);
		spMemberTable.setToolTipText("Double click an entry to see its details");
		//spMemberTable.setBorder(new TitledBorder("List of Members"));
		spMemberTable.setPreferredSize(new Dimension(400, 220));
		splitPane_right.setTopComponent(spMemberTable);
		
		memberTable.addMouseListener(new MouseAdapter() {
			@Override
			public void mouseClicked(MouseEvent e) {
				if(e.getClickCount() == 2)
				{
					JTable t = (JTable)e.getSource();					
					String urn = (String)(t.getValueAt(t.getSelectedRow(),t.getSelectedColumn()));
					if(urn.startsWith("urn:"))
					{
						String username = urn.substring(urn.lastIndexOf('+')+1);
						mainGUI.setSelectedMember(username);
					}
				}				
			}
		});
		
		projectList.addListSelectionListener( new ListSelectionListener() {

            @Override
            public void valueChanged(ListSelectionEvent arg0) {
                if (!arg0.getValueIsAdjusting()) {
                  
                  Project d = (Project) projectList.getSelectedValue();
                  textAreaDesc.setText(d.desc);
                  textFieldExpiry.setText(Utils.utcTolocal(d.expiry));
                  textFieldProjectURN.setText(d.urn);
                  textFieldCreation.setText(Utils.utcTolocal(d.creation));
                  
                  //if(d.members.size() == 0)
                  LinkedList<Membership> members = SliceAuthorityAPI.lookupMembers(d.urn, "PROJECT");
                  if(members == null)
                  {
                	  showErrorMessage();
                	  return;
                  }
                  d.members = members;
                  tableModel.clear();
                  for(int i=0; i<members.size(); i++)
                	  tableModel.add(members.get(i).urn, members.get(i).role);

                  Slice[] slices = SliceAuthorityAPI.lookupSlices(d.urn);
                  if(slices == null)
                  {
                	  showErrorMessage();
                	  return;
                  }
                  d.slices = slices;
                  projectSliceListModel.clear();
                  for(int i=0; i<slices.length; i++)
                	  projectSliceListModel.add(slices[i].name);
                }
            }
        }); 
		
		projectSliceListModel = new SortedListModel<String>();
		projectSliceList = new JList(projectSliceListModel);
		projectSliceList.setToolTipText("Double click an entry to see its details");
		projectSliceList.addMouseListener(new MouseAdapter() {
			@Override
			public void mouseClicked(MouseEvent e) {
				if(e.getClickCount() == 2)
				{
					mainGUI.setSelectedSlice((String)((JList)e.getSource()).getSelectedValue());
				}			
			}
		});
		
		
		
		JPanel panelButtons = new JPanel();
		add(panelButtons, BorderLayout.SOUTH);
		
		JButton btnAddMember = new JButton("Add Member");
		btnAddMember.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent arg0) {
				if(projectList.isSelectionEmpty())
					JOptionPane.showMessageDialog(null, "Select the project from list to add member.");
				else
					showAddMemberDialog();
			}
		});
		
		JButton btnNewProject = new JButton("New Project");
		btnNewProject.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent arg0) {
				Project d = showNewProjectDialog();
				
				if(d == null)
					return;
				
				d = SliceAuthorityAPI.addProject(d);
				if(d != null)
				{					
					projectListModel.add(d);
					projectList.setSelectedValue(d, true);
				}else
					showErrorMessage();
				
			}
		});
		panelButtons.add(btnNewProject);
		
		JButton btnDeleteProject = new JButton("Delete Project");
		btnDeleteProject.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent arg0) {
				
				if(projectList.isSelectionEmpty())
				{
					JOptionPane.showMessageDialog(Projects.this, "Select a project to delete.");
					return;
				}
				
				Project project = (Project) projectList.getSelectedValue();
				
				if(project.slices.length > 0)
				{
					JOptionPane.showMessageDialog(Projects.this, "Cannot delete a project containing slices.", "Delete Project", JOptionPane.INFORMATION_MESSAGE);
					return;					
				}
				
				boolean rsp = SliceAuthorityAPI.delProject(project.urn);
				if(rsp)
				{
					projectListModel.removeElement(project);
				}else
					showErrorMessage();
				
			}
		});
		panelButtons.add(btnDeleteProject);
		panelButtons.add(btnAddMember);
		
		JButton btnRemoveMember = new JButton("Remove Member");
		btnRemoveMember.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent arg0) {
				if(memberTable.getSelectedRow()>=0)
				{
					Project project = (Project) projectList.getSelectedValue();
					int row = memberTable.convertRowIndexToModel(memberTable.getSelectedRow());
					Membership mem = project.members.get(row);
					
					if(mem.role.toUpperCase().equals("LEAD"))
					{
						JOptionPane.showMessageDialog(Projects.this, "A member with LEAD role cannot be removed.", "Remove Member", JOptionPane.INFORMATION_MESSAGE);
					}
					else
					{					
						boolean rsp = SliceAuthorityAPI.removeMember(project.urn, mem.urn, mem.type);
						if(rsp)
						{
							project.members.remove(row);
							tableModel.remove(row);
						}else
							showErrorMessage();
					}
				}
				else
					JOptionPane.showMessageDialog(Projects.this, "Select a member from list to remove.", "Remove Member", JOptionPane.INFORMATION_MESSAGE);
				
			}
		});
		panelButtons.add(btnRemoveMember);
		
		JButton btnRole = new JButton("Alter Role");
		btnRole.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent arg0) {
				if(memberTable.getSelectedRow()>=0)
					showChangeRoleDialog();
				else
					JOptionPane.showMessageDialog(Projects.this, "Select the member from list to change role.", "Alter Role", JOptionPane.INFORMATION_MESSAGE);
			}
		});
		panelButtons.add(btnRole);
		JScrollPane sp = new JScrollPane(projectSliceList);
		sp.setPreferredSize(new Dimension(400, 220));
		sp.setBorder(new TitledBorder("List of Project Slices"));
		splitPane_right.setBottomComponent(sp);
		
		JSplitPane splitPane = new JSplitPane();
		splitPane.setRightComponent(rightPanel);
		splitPane.setLeftComponent(scrollPane);		
		add(splitPane, BorderLayout.CENTER);

		
		//Select first element in the list for display
		if(projectListModel.getSize()>0)
			projectList.setSelectedIndex(0);

	}
	
	
	private Project showNewProjectDialog()
	{
		JPanel infoPanel = new JPanel();
		infoPanel.setLayout(new GridBagLayout());
		
		GridBagConstraints c = new GridBagConstraints();
		c.fill = GridBagConstraints.HORIZONTAL;
		c.insets = new Insets(10,0,0,0);  //top padding
		c.weightx = 0.1;
		c.gridx = 0;
		c.gridy = 0;				
		infoPanel.add(new JLabel("Name:"),c);
		c.gridy = 1;						
		infoPanel.add(new JLabel("Description:"),c);
		
		JTextField name;
		JTextArea desc;
		name = new JTextField("");
		name.setColumns(30);
	    AbstractDocument doc = (AbstractDocument) name.getDocument();
	    doc.setDocumentFilter(new PatternFilter("^[a-zA-Z0-9][-a-zA-Z0-9]{0,18}"));
		
		desc = new JTextArea("");
		
		c.weightx = 0.9;
		c.gridx = 1;
		c.gridy = 0;		
		infoPanel.add(name, c);
		c.gridy = 1;		
		c.ipady = 100;
		infoPanel.add(new JScrollPane(desc), c);		
		
		int response; 
		do{
			response = JOptionPane.showConfirmDialog(this, infoPanel, "New Project",
					JOptionPane.OK_CANCEL_OPTION, JOptionPane.PLAIN_MESSAGE);
			name.setBackground(name.getText().trim().length()==0?Color.pink:Color.white);
			desc.setBackground(desc.getText().trim().length()==0?Color.pink:Color.white);
		}
		while( (name.getText().length()==0   ||
			    desc.getText().length()==0 ) &&	
			   response == JOptionPane.OK_OPTION);
		
		if(response != JOptionPane.OK_OPTION)
			return null;
		else
		{
			Project d = new Project();
			d.name = name.getText().trim();
			d.desc = desc.getText().trim();
			
			return d;
		}
		
	}
	
	private void showAddMemberDialog()
	{
		Project project = (Project) projectList.getSelectedValue();
		HashSet<String> existingMembers = new HashSet<String>();
		for(int i=0; i<project.members.size(); i++)
			existingMembers.add(project.members.get(i).urn);
		
		HashSet<String> nonMembers = new HashSet<String>();
		Object[] allMembers = mainGUI.getMembersArray();
		for(int i=0; i<allMembers.length; i++)
		{
			Member m = (Member)allMembers[i];
			
			//Ignore Revoked members
			if(MemberAuthorityAPI.crl.getRevokedCertificate(m.cert) != null)
				continue;
			
			String urn = m.urn;
			if(!existingMembers.contains(urn))
				nonMembers.add(urn);
		}
		
		String[] choiceArray = nonMembers.toArray(new String[0]);
		if(choiceArray.length == 0)
		{
			JOptionPane.showMessageDialog(this, "There are no more ACTIVE members to add to this project.", "Add Member", JOptionPane.INFORMATION_MESSAGE);
		}
		else
		{
			String newMember = (String) JOptionPane.showInputDialog(null, "Select new member for project "+project.name+"\n", "Add Member", JOptionPane.PLAIN_MESSAGE, null, choiceArray, choiceArray[0]);
			if(newMember != null)
			{
				Membership mem = SliceAuthorityAPI.addMember(project.urn, newMember, "PROJECT");
				if(mem!=null)
				{
					tableModel.add(newMember, "MEMBER");
					project.members.add(mem);
				}
				else
					showErrorMessage();
			}
		}
		
		
	}
	
	private void showChangeRoleDialog()
	{
		Project project = (Project) projectList.getSelectedValue();
		int row = memberTable.convertRowIndexToModel(memberTable.getSelectedRow());
		Membership m = project.members.get(row);
		String role = project.members.get(row).role;
		String availableRoles[];
		
		
		if( role.equals("MEMBER"))
			availableRoles = new String[]{"LEAD", "ADMIN"};
		else if( role.equals("ADMIN"))
			availableRoles = new String[]{"LEAD", "MEMBER"};
		else
		{
			JOptionPane.showMessageDialog(this, "There must always be a LEAD role for a project.\nAssigning LEAD role to another member would automatically change this user's role to MEMBER.","Alter Role", JOptionPane.INFORMATION_MESSAGE);
			return;
		}
		
		String newRole = (String) JOptionPane.showInputDialog(this, "Select new role member:", "Change Member Role", JOptionPane.PLAIN_MESSAGE, null, availableRoles, availableRoles[0]);
		if(newRole != null)
		{
			Membership rsp = SliceAuthorityAPI.changeMemberRole(project.urn, m.urn , newRole, m.type);
			if(rsp != null)
			{
				//Let's perform a lookup again to get a fresh member list
				LinkedList<Membership> members = SliceAuthorityAPI.lookupMembers(project.urn, m.type);
				if(members == null)
					return;
				
				project.members = members;				
                tableModel.clear();
                for(int i=0; i<project.members.size(); i++)
              	  tableModel.add(project.members.get(i).urn, project.members.get(i).role);
			}
			else
				showErrorMessage();			
		}
		
	}

	private void showErrorMessage()
	{
		JOptionPane.showMessageDialog(
			    this, 
			    "<html><body><p style='width: 300px;'>"+SliceAuthorityAPI.output+"</p></body></html>", 
			    "Error", 
			    JOptionPane.ERROR_MESSAGE);
	}
	
	public Object[] getProjectArray()
	{
		return projectListModel.toArray();
	}
} //class


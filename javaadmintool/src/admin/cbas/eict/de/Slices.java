package admin.cbas.eict.de;

import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.Dimension;

import javax.swing.JComboBox;
import javax.swing.JList;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.ListSelectionModel;
import javax.swing.border.TitledBorder;
import javax.swing.event.ListSelectionEvent;
import javax.swing.event.ListSelectionListener;
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

import javax.swing.SwingConstants;
import javax.swing.JTextArea;

import admin.cbas.eict.de.MemberAuthorityAPI.Member;
import admin.cbas.eict.de.SliceAuthorityAPI.Membership;
import admin.cbas.eict.de.SliceAuthorityAPI.Project;
import admin.cbas.eict.de.SliceAuthorityAPI.Slice;

import java.awt.event.ActionListener;
import java.awt.event.ActionEvent;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;

public class Slices extends JPanel {

	private static final long serialVersionUID = 5788915620169210764L;
	JList sliceList;
	SortedListModel<Slice> sliceListModel;
	private JTable memberTable;
	private JTextField textFieldSliceURN;
	private JTextField textFieldProjectURN;
	private JTextField textFieldExpiry, textFieldCreation;
	private JTextArea textAreaDesc;
	MemberTableModel tableModel;
	final MainGUI mainGUI;

	/**
	 * Create the frame.
	 */
	public Slices(MainGUI parent, Slice[] sliceData) {
		
		mainGUI = parent;
		setLayout(new BorderLayout(0, 0));
				
		JScrollPane scrollPane = new JScrollPane();
		sliceListModel = new SortedListModel<Slice>();
		if(sliceData != null)
			sliceListModel.addAll(sliceData);
		
		sliceList = new JList(sliceListModel);
		sliceList.setSelectionMode(ListSelectionModel.SINGLE_SELECTION);
		scrollPane.setViewportView(sliceList);
		TitledBorder titled = new TitledBorder("List of Slices");
		scrollPane.setBorder(titled);
		scrollPane.setPreferredSize(new Dimension(300,400));
		
		
		JSplitPane splitPane = new JSplitPane();
		splitPane.setLeftComponent(scrollPane);
		add(splitPane, BorderLayout.CENTER);
		
		JPanel rightPanel = new JPanel();
		splitPane.setRightComponent(rightPanel);
		rightPanel.setLayout(new BorderLayout(0, 0));
		
		JPanel panelInfo = new JPanel();
		rightPanel.add(panelInfo, BorderLayout.NORTH);
		GridBagLayout gbl_panelInfo = new GridBagLayout();
		gbl_panelInfo.rowWeights = new double[]{0.0, 0.0, 0.0, 1.0};
		gbl_panelInfo.columnWeights = new double[]{0.0, 1.0};
		panelInfo.setLayout(gbl_panelInfo);
		
		JLabel lblURN = new JLabel("URN:");
		lblURN.setHorizontalAlignment(SwingConstants.TRAILING);
		GridBagConstraints gbc_lblURN = new GridBagConstraints();
		gbc_lblURN.insets = new Insets(5, 0, 5, 5);
		gbc_lblURN.weightx = 0.01;
		gbc_lblURN.anchor = GridBagConstraints.EAST;
		gbc_lblURN.gridx = 0;
		gbc_lblURN.gridy = 0;
		panelInfo.add(lblURN, gbc_lblURN);
		
		textFieldSliceURN = new JTextField();
		textFieldSliceURN.setEditable(false);
		GridBagConstraints gbc_textFieldSliceURN = new GridBagConstraints();
		gbc_textFieldSliceURN.insets = new Insets(5, 0, 5, 0);
		gbc_textFieldSliceURN.weightx = 0.99;
		gbc_textFieldSliceURN.fill = GridBagConstraints.HORIZONTAL;
		gbc_textFieldSliceURN.gridx = 1;
		gbc_textFieldSliceURN.gridy = 0;
		panelInfo.add(textFieldSliceURN, gbc_textFieldSliceURN);
		
		
		JLabel lblNewLabel = new JLabel("Project:");
		GridBagConstraints gbc_lblNewLabel = new GridBagConstraints();
		gbc_lblNewLabel.insets = new Insets(10, 0, 5, 5);
		gbc_lblNewLabel.weightx = 0.01;
		gbc_lblNewLabel.anchor = GridBagConstraints.EAST;
		gbc_lblNewLabel.gridx = 0;
		gbc_lblNewLabel.gridy = 1;
		panelInfo.add(lblNewLabel, gbc_lblNewLabel);
		
		textFieldProjectURN = new JTextField();
		textFieldProjectURN.setEditable(false);
		GridBagConstraints gbc_textFieldProjectURN = new GridBagConstraints();
		gbc_textFieldProjectURN.insets = new Insets(10, 0, 5, 0);
		
		gbc_textFieldProjectURN.weightx = 0.99;
		gbc_textFieldProjectURN.fill = GridBagConstraints.HORIZONTAL;
		gbc_textFieldProjectURN.gridx = 1;
		gbc_textFieldProjectURN.gridy = 1;
		panelInfo.add(textFieldProjectURN, gbc_textFieldProjectURN);
		
		JLabel lblCreation = new JLabel("Creation:");
		GridBagConstraints gbc_lblCreation = new GridBagConstraints();
		gbc_lblCreation.anchor = GridBagConstraints.EAST;
		gbc_lblCreation.insets = new Insets(10, 0, 0, 5);
		gbc_lblCreation.gridx = 0;
		gbc_lblCreation.gridy = 2;
		panelInfo.add(lblCreation, gbc_lblCreation);
		
		textFieldCreation = new JTextField();		
		textFieldCreation.setEditable(false);
		GridBagConstraints gbc_textFieldCreation = new GridBagConstraints();
		gbc_textFieldCreation.insets = new Insets(10, 0, 5, 0);
		gbc_textFieldCreation.weightx = 0.99;
		gbc_textFieldCreation.fill = GridBagConstraints.HORIZONTAL;
		gbc_textFieldCreation.gridx = 1;
		gbc_textFieldCreation.gridy = 2;
		panelInfo.add(textFieldCreation, gbc_textFieldCreation);

		
		JLabel lblNewLabel_1 = new JLabel("Expiration:");
		GridBagConstraints gbc_lblNewLabel_1 = new GridBagConstraints();
		gbc_lblNewLabel_1.insets = new Insets(10, 0, 0, 5);
		gbc_lblNewLabel_1.weightx = 0.01;
		gbc_lblNewLabel_1.anchor = GridBagConstraints.EAST;
		
		gbc_lblNewLabel_1.gridx = 0;
		gbc_lblNewLabel_1.gridy = 3;
		panelInfo.add(lblNewLabel_1, gbc_lblNewLabel_1);
		
		textFieldExpiry = new JTextField();
		textFieldExpiry.setEditable(false);
		GridBagConstraints gbc_textFieldExpiry = new GridBagConstraints();
		gbc_textFieldExpiry.insets = new Insets(10, 0, 0, 0);
		gbc_textFieldExpiry.weightx = 0.99;
		gbc_textFieldExpiry.fill = GridBagConstraints.HORIZONTAL;
		gbc_textFieldExpiry.gridx = 1;
		gbc_textFieldExpiry.gridy = 3;
		panelInfo.add(textFieldExpiry, gbc_textFieldExpiry);
		
		JLabel lblSliceDescription = new JLabel("Description:");
		GridBagConstraints gbc_lblSliceDescription = new GridBagConstraints();
		gbc_lblSliceDescription.insets = new Insets(10, 0, 20, 5);
		gbc_lblSliceDescription.gridx = 0;
		gbc_lblSliceDescription.gridy = 4;
		panelInfo.add(lblSliceDescription, gbc_lblSliceDescription);
		
		textAreaDesc = new JTextArea();
		textAreaDesc.setEditable(false);
		GridBagConstraints gbc_textArea = new GridBagConstraints();
		gbc_textArea.fill = GridBagConstraints.BOTH;
		gbc_textArea.insets = new Insets(10, 0, 20, 5);
		gbc_textArea.gridx = 1;
		gbc_textArea.gridy = 4;
		gbc_textArea.ipady = 40;
		panelInfo.add(new JScrollPane(textAreaDesc), gbc_textArea);
		
		
		JPanel panelButtons = new JPanel();
		rightPanel.add(panelButtons, BorderLayout.SOUTH);
		
		JButton btnAddMember = new JButton("Add Member");
		btnAddMember.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent arg0) {
				if(sliceList.isSelectionEmpty())
					JOptionPane.showMessageDialog(null, "Select the slice from list to add member.");
				else
					showAddMemberDialog();
			}
		});
		
		JButton btnNewSlice = new JButton("New Slice");
		btnNewSlice.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent arg0) {
				Slice d = showNewSliceDialog();
				if (d != null)
				{
					d = SliceAuthorityAPI.addSlice(d);
					if(d == null)						
						showErrorMessage();
					else
					{
						sliceListModel.add(d);
						sliceList.setSelectedValue(d.name, true);
					}
				}
			}
		});
		panelButtons.add(btnNewSlice);
		panelButtons.add(btnAddMember);
		
		JButton btnRemoveMember = new JButton("Remove Member");
		btnRemoveMember.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent arg0) {
				if(memberTable.getSelectedRow()>=0)
				{
					Slice slice = (Slice) sliceList.getSelectedValue();
					int row = memberTable.getSelectedRow();
					String role = slice.members.get(row).role;
					
					if(role.toUpperCase().equals("LEAD"))
					{
						JOptionPane.showMessageDialog(null, "Sorry, a member with LEAD role cannot be removed.");
					}
					else
					{					
						boolean rsp = SliceAuthorityAPI.removeMember(slice.urn, slice.members.get(row).urn, slice.members.get(row).type);
						if(rsp)
						{
							slice.members.remove(row);
							tableModel.remove(row);
						}
						else
							showErrorMessage();
					}
				}
				else
					JOptionPane.showMessageDialog(null, "Select a member from list to remove.");
				
			}
		});
		panelButtons.add(btnRemoveMember);
		
		JButton btnRole = new JButton("Alter Role");
		btnRole.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent arg0) {
				if(memberTable.getSelectedRow()>=0)
					showChangeRoleDialog();
				else
					JOptionPane.showMessageDialog(null, "Select the member from list to change role.");
			}
		});
		panelButtons.add(btnRole);
		
		
		tableModel = new MemberTableModel(null, new String[]{"Member", "Role"});		
		memberTable = new JTable(tableModel);
		memberTable.addMouseListener(new MouseAdapter() {
			@Override
			public void mouseClicked(MouseEvent e) {
				if(e.getClickCount() == 2)
				{
					int row = ((JTable)e.getSource()).getSelectedRow();
					String urn = (String)((JTable)e.getSource()).getModel().getValueAt(row, 0);
					String username = urn.substring(urn.lastIndexOf('+')+1);
					mainGUI.setSelectedMember(username);
				}				
			}
		});
		memberTable.setSelectionMode(ListSelectionModel.SINGLE_SELECTION);
		memberTable.getColumnModel().getColumn(0).setPreferredWidth(300);
		memberTable.getColumnModel().getColumn(1).setPreferredWidth(75);
		memberTable.getColumnModel().getColumn(1).setMaxWidth(75);
		JScrollPane memberScrollPane = new JScrollPane(memberTable);
		memberScrollPane.setToolTipText("Double click an entry to see its details");
		rightPanel.add(memberScrollPane, BorderLayout.CENTER);
		
		sliceList.addListSelectionListener( new ListSelectionListener() {

            @Override
            public void valueChanged(ListSelectionEvent arg0) {
                if (!arg0.getValueIsAdjusting()) {

                  Slice d = (Slice) sliceList.getSelectedValue();
                  textFieldSliceURN.setText(d.urn);
                  textAreaDesc.setText(d.desc);
                  textFieldExpiry.setText(Utils.utcTolocal(d.expiry));
                  textFieldCreation.setText(Utils.utcTolocal(d.creation));
                  textFieldProjectURN.setText(d.urnProject);
                  tableModel.clear();
                  //if(d.members.size() == 0)
                  LinkedList<Membership> members = SliceAuthorityAPI.lookupMembers(d.urn, "SLICE");
                  if(members == null)
                  {
                	  showErrorMessage();
                	  return;
                  }
                  d.members = members;
                  
                  for(int i=0; i<members.size(); i++){
                	  tableModel.add(members.get(i).urn, members.get(i).role);
                  }
                }
            }
        }); 
		
		//Select first item for display
		if(sliceListModel.getSize()>0)
			sliceList.setSelectedIndex(0);

		
	}
	
	
	private Slice showNewSliceDialog()
	{
		Object[] allProjects = mainGUI.getProjectsArray();
		
		if(allProjects.length == 0)
		{
			JOptionPane.showMessageDialog(this, "Please first create a project.");
			return null;
		}
		
		String[] projectNames = new String[allProjects.length];
		for(int i=0; i< projectNames.length; i++)
			projectNames[i] = ((Project)allProjects[i]).name;
		
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
		infoPanel.add(new JLabel("Project:"),c);
		c.gridy = 2;						
		infoPanel.add(new JLabel("Description:"),c);
		
		JComboBox projectBox = new JComboBox(projectNames);
		JTextField name = new JTextField("");
		name.setColumns(30);
		JTextArea desc = new JTextArea("");
		
		c.weightx = 0.9;
		c.gridx = 1;
		c.gridy = 0;		
		infoPanel.add(name, c);
		c.gridy = 1;		
		infoPanel.add(projectBox, c);
		c.gridy = 2;		
		c.ipady = 100;
		infoPanel.add(new JScrollPane(desc), c);		
		
		int response; 
		do{
			response = JOptionPane.showConfirmDialog(this, infoPanel, "New Slice",
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
			Slice d = new Slice();
			d.name = name.getText().trim();
			d.desc = desc.getText().trim();
			d.urnProject = ((Project)allProjects[projectBox.getSelectedIndex()]).urn;
			return d;
		}
		
	}
	
	private void showAddMemberDialog()
	{		
		Slice slice = (Slice) sliceList.getSelectedValue();
		HashSet<String> existingMembers = new HashSet<String>();
		for(int i=0; i<slice.members.size(); i++)
			existingMembers.add(slice.members.get(i).urn);
		
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
			JOptionPane.showMessageDialog(null, "There are no more members to add to this slice.");
		}
		else
		{
			String newMember = (String) JOptionPane.showInputDialog(null, "Select new member for slice "+slice.name+"\n", "Add Member", JOptionPane.PLAIN_MESSAGE, null, choiceArray, choiceArray[0]);
			if(newMember != null)
			{
				Membership mem = SliceAuthorityAPI.addMember(slice.urn, newMember, "SLICE");
				if(mem != null)
				{
					tableModel.add(newMember, "MEMBER");
					slice.members.add(mem);
				}
				else
					showErrorMessage();
			}
		}
		
		
	}
	
	private void showChangeRoleDialog()
	{
		Slice slice = (Slice) sliceList.getSelectedValue();
		int row = memberTable.getSelectedRow();
		String role = slice.members.get(row).role;
		String availableRoles[];
		
		if( role.equals("MEMBER"))
			availableRoles = new String[]{"LEAD", "ADMIN"};
		else if( role.equals("ADMIN"))
			availableRoles = new String[]{"LEAD", "MEMBER"};
		else
		{
			JOptionPane.showMessageDialog(this, "There must always be a LEAD role for a slice.\nAssigning LEAD role to another member would automatically change this user's role to MEMBER.");
			return;
		}
		
		String newRole = (String) JOptionPane.showInputDialog(null, "Select new role member:", "Change Member Role", JOptionPane.PLAIN_MESSAGE, null, availableRoles, availableRoles[0]);
		if(newRole != null)
		{
			Membership rsp = SliceAuthorityAPI.changeMemberRole(slice.urn, slice.members.get(row).urn , newRole, slice.members.get(row).type);
			if(rsp != null)
			{
				//Let's perform a lookup again to get a fresh member list
                LinkedList<Membership> members = SliceAuthorityAPI.lookupMembers(slice.urn, slice.members.get(row).type);
                if(members == null)
                	return;
                slice.members = members;                
                tableModel.clear();
                for(int i=0; i<slice.members.size(); i++)
              	  tableModel.add(slice.members.get(i).urn, slice.members.get(i).role);
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

	public Object[] getSliceArray()
	{
		return sliceListModel.toArray();
	}
	
	
} //class



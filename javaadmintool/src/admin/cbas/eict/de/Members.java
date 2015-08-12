package admin.cbas.eict.de;

import java.awt.Color;
import java.awt.Dimension;
import java.awt.FlowLayout;
import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.GridLayout;
import java.awt.Insets;

import javax.swing.AbstractAction;
import javax.swing.Action;
import javax.swing.ActionMap;
import javax.swing.DefaultListModel;
import javax.swing.DropMode;
import javax.swing.JButton;
import javax.swing.JCheckBox;
import javax.swing.JDialog;
import javax.swing.JFileChooser;
import javax.swing.JLabel;
import javax.swing.JOptionPane;
import javax.swing.JScrollPane;
import javax.swing.JSplitPane;
import javax.swing.JTextField;
import javax.swing.TransferHandler;

import java.awt.BorderLayout;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.PrintWriter;
import java.security.cert.X509CRLEntry;
import java.util.Arrays;
import java.util.LinkedList;

import javax.swing.JPanel;
import javax.swing.JList;
import javax.swing.ListSelectionModel;
import javax.swing.border.TitledBorder;
import javax.swing.event.ListSelectionEvent;
import javax.swing.event.ListSelectionListener;
import javax.swing.text.AbstractDocument;

import admin.cbas.eict.de.MemberAuthorityAPI.Member;
import admin.cbas.eict.de.SliceAuthorityAPI.AnObject;

import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;

import javax.swing.JTextArea;

public class Members extends JPanel{
	
	private static final long serialVersionUID = -2394649760751128917L;
	JList userList;
	JButton buttonEditUser, buttonAddUser, buttonRevokeUser, buttonExtendMembership;
	SortedListModel<MemberAuthorityAPI.Member> listModelMembers;
	SortedListModel<String> listModelProjects, listModelSlices;
	private JPanel panelRight;
	private JSplitPane splitPaneProjectSlices;
	private JScrollPane scrollPaneProjects;
	private JList listProjects, listSlices;
	private JScrollPane scrollPaneSlices;
	private JLabel lblFirstName;
	private JTextField tfFirstName;
	private JLabel lblEmail;
	private JTextField tfEmail;
	private JLabel lblUrn;
	private JTextField tfUserURN;
	private JLabel lblCertificateCreation;
	private JTextField tfValidFrom;
	private JLabel lblCertificateExpiration;
	private JTextField tfValidUntil;
	private JLabel lblMembershipStatus;
	private JTextField tfMembershipStatus;
	JFileChooser fileChooser;
	static Color DARK_GREEN = new Color(30,200,60);
	final MainGUI mainGUI;
	private JLabel lblPrivileges;
	private JTextArea taPrivileges;
	private JButton btnManagePrivileges;
	private JLabel lblPublicSshKey;
	private JTextArea taSshKey;
	private JButton btnEditSshKey;

	/**
	 * Create the application.
	 */
	public Members(MainGUI mainWindow, Member[] memberData) {
		
		mainGUI = mainWindow;
			
		setLayout(new BorderLayout());
		
		JScrollPane scrollPane = new JScrollPane();
		listModelMembers = new SortedListModel<Member>();
		if(memberData != null)
			listModelMembers.addAll(memberData);
		userList = new JList(listModelMembers);
		userList.setSelectionMode(ListSelectionModel.SINGLE_SELECTION);
		scrollPane.setViewportView(userList);
		TitledBorder titled = new TitledBorder("List of Members");
		scrollPane.setBorder(titled);
		scrollPane.setPreferredSize(new Dimension(200,400));
		scrollPane.setMinimumSize(new Dimension(200,400));
		buttonEditUser = new JButton("Edit Info");
		buttonEditUser.addActionListener( new ActionListener(){
			@Override
			public void actionPerformed(ActionEvent arg0) {
				
				if(userList.isSelectionEmpty())
				{
					JOptionPane.showMessageDialog(Members.this, "Select a user from list to edit.", "Edit info", JOptionPane.INFORMATION_MESSAGE);
					return;
				}
				
				Member toEdit = (Member) userList.getSelectedValue();
				Member changes = getMemberDetailInput(toEdit);
				if( changes != null)
				{
					changes.urn = toEdit.urn;
					boolean rsp = MemberAuthorityAPI.updateMemberInfo(changes);
					if(rsp == true)
					{						
						toEdit.fName = changes.fName;
						toEdit.lName = changes.lName;
						toEdit.email = changes.email;
		                tfFirstName.setText(changes.fName+" "+changes.lName);
		                tfEmail.setText(changes.email);
					}
					else
						showErrorMessage();
				}
			}			
		});
		
		buttonRevokeUser = new JButton("Revoke Certificate");
		buttonRevokeUser.addActionListener( new ActionListener(){
			@Override
			public void actionPerformed(ActionEvent arg0) {
				
				if(userList.isSelectionEmpty())
				{
					JOptionPane.showMessageDialog(Members.this, "First select a user from list.", "Revoke Certificate", JOptionPane.INFORMATION_MESSAGE);
					return;
				}
				

				Member toRevoke = (Member) userList.getSelectedValue();
                X509CRLEntry e = MemberAuthorityAPI.crl.getRevokedCertificate(toRevoke.cert);
                
                if(e!=null)
                {
					JOptionPane.showMessageDialog(Members.this, "The certificate is already in revoked state.", "Revoke Certificate", JOptionPane.INFORMATION_MESSAGE);
					return;                	
                }
                
				
				if(toRevoke.username.equals("root") || toRevoke.username.equals("expedient"))
				{
					JOptionPane.showMessageDialog(Members.this, toRevoke.username+" is a privileged user. This membership cannot be revoked.", "Revoke Certificate", JOptionPane.INFORMATION_MESSAGE);
					return;                						
				}
				
				
				boolean rsp = MemberAuthorityAPI.reovkeMembership(toRevoke);
				if(rsp == true)
				{
	                  e = MemberAuthorityAPI.crl.getRevokedCertificate(toRevoke.cert);
	                  tfMembershipStatus.setText(e==null?"Active":"Revoked");
	                  tfMembershipStatus.setForeground(e==null?DARK_GREEN:Color.RED);
				}
				else
					showErrorMessage();
									
			}			
		});		
		buttonExtendMembership = new JButton("Renew Certificate");
		buttonExtendMembership.addActionListener( new ActionListener(){
			@Override
			public void actionPerformed(ActionEvent arg0) {

				if(userList.isSelectionEmpty())
				{
					JOptionPane.showMessageDialog(Members.this, "First select a user from list.", "Renew Certificate", JOptionPane.INFORMATION_MESSAGE);
					return;
				}
				

				Member toRenew = (Member) userList.getSelectedValue();
				
				if(toRenew.username.equals("root") || toRenew.username.equals("expedient"))
				{
					JOptionPane.showMessageDialog(Members.this, toRenew.username+" is a privileged user. This membership cannot be modified.", "Renew Certificate", JOptionPane.INFORMATION_MESSAGE);
					return;                						
				}
				
				Member rsp = MemberAuthorityAPI.extendMembership(toRenew);
				if(rsp != null)
				{
					toRenew.cert = rsp.cert;
					toRenew.certStr = rsp.certStr;
					toRenew.privateKey = rsp.privateKey;
					saveCertificateAndKey(toRenew, "Membership has been extended.");
	                tfValidFrom.setText(Utils.formatDate(toRenew.cert.getNotBefore()));
	                tfValidUntil.setText(Utils.formatDate(toRenew.cert.getNotAfter()));
	                tfMembershipStatus.setText("Active");	
	                tfMembershipStatus.setForeground(DARK_GREEN);
				}
				else
					showErrorMessage();
									
			}			
		});
		
		panelRight = new JPanel();		
		panelRight.setLayout(new BorderLayout(0, 0));
		
		JPanel infoPanel = new JPanel();
		panelRight.add(infoPanel, BorderLayout.NORTH);
		infoPanel.setBorder(new TitledBorder("Member Information"));
		GridBagLayout gbl_infoPanel = new GridBagLayout();
		gbl_infoPanel.rowWeights = new double[]{0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0};
		gbl_infoPanel.columnWeights = new double[]{0.0, 1.0};
		infoPanel.setLayout(gbl_infoPanel);
		
		lblFirstName = new JLabel("Name:");
		GridBagConstraints gbc_lblName = new GridBagConstraints();
		gbc_lblName.insets = new Insets(0, 0, 7, 5);
		gbc_lblName.anchor = GridBagConstraints.EAST;
		gbc_lblName.gridx = 0;
		gbc_lblName.gridy = 0;
		infoPanel.add(lblFirstName, gbc_lblName);
		
		tfFirstName = new JTextField();
		tfFirstName.setEditable(false);
		GridBagConstraints gbc_tfFirstName = new GridBagConstraints();
		gbc_tfFirstName.insets = new Insets(0, 0, 7, 0);
		gbc_tfFirstName.fill = GridBagConstraints.HORIZONTAL;
		gbc_tfFirstName.gridx = 1;
		gbc_tfFirstName.gridy = 0;
		infoPanel.add(tfFirstName, gbc_tfFirstName);
		tfFirstName.setColumns(10);
		
		lblEmail = new JLabel("Email:");
		GridBagConstraints gbc_lblEmail = new GridBagConstraints();
		gbc_lblEmail.anchor = GridBagConstraints.EAST;
		gbc_lblEmail.insets = new Insets(0, 0, 7, 5);
		gbc_lblEmail.gridx = 0;
		gbc_lblEmail.gridy = 1;
		infoPanel.add(lblEmail, gbc_lblEmail);
		
		tfEmail = new JTextField();
		tfEmail.setEditable(false);
		GridBagConstraints gbc_tfEmail = new GridBagConstraints();
		gbc_tfEmail.insets = new Insets(0, 0, 7, 0);
		gbc_tfEmail.fill = GridBagConstraints.HORIZONTAL;
		gbc_tfEmail.gridx = 1;
		gbc_tfEmail.gridy = 1;
		infoPanel.add(tfEmail, gbc_tfEmail);
		tfEmail.setColumns(10);
		
		lblUrn = new JLabel("URN:");
		GridBagConstraints gbc_lblUrn = new GridBagConstraints();
		gbc_lblUrn.anchor = GridBagConstraints.EAST;
		gbc_lblUrn.insets = new Insets(0, 0, 7, 5);
		gbc_lblUrn.gridx = 0;
		gbc_lblUrn.gridy = 2;
		infoPanel.add(lblUrn, gbc_lblUrn);
		
		tfUserURN = new JTextField();
		tfUserURN.setEditable(false);
		GridBagConstraints gbc_tfUserURN = new GridBagConstraints();
		gbc_tfUserURN.insets = new Insets(0, 0, 7, 0);
		gbc_tfUserURN.fill = GridBagConstraints.HORIZONTAL;
		gbc_tfUserURN.gridx = 1;
		gbc_tfUserURN.gridy = 2;
		infoPanel.add(tfUserURN, gbc_tfUserURN);
		tfUserURN.setColumns(10);
		
		lblCertificateCreation = new JLabel("Certificate Creation:");
		GridBagConstraints gbc_lblCertificateCreation = new GridBagConstraints();
		gbc_lblCertificateCreation.anchor = GridBagConstraints.EAST;
		gbc_lblCertificateCreation.insets = new Insets(0, 0, 7, 5);
		gbc_lblCertificateCreation.gridx = 0;
		gbc_lblCertificateCreation.gridy = 3;
		infoPanel.add(lblCertificateCreation, gbc_lblCertificateCreation);
		
		tfValidFrom = new JTextField();
		tfValidFrom.setEditable(false);
		GridBagConstraints gbc_tfValidFrom = new GridBagConstraints();
		gbc_tfValidFrom.insets = new Insets(0, 0, 7, 0);
		gbc_tfValidFrom.fill = GridBagConstraints.HORIZONTAL;
		gbc_tfValidFrom.gridx = 1;
		gbc_tfValidFrom.gridy = 3;
		infoPanel.add(tfValidFrom, gbc_tfValidFrom);
		tfValidFrom.setColumns(10);
		
		lblCertificateExpiration = new JLabel("Certificate Expiration:");
		GridBagConstraints gbc_lblCertificateExpiration = new GridBagConstraints();
		gbc_lblCertificateExpiration.anchor = GridBagConstraints.EAST;
		gbc_lblCertificateExpiration.insets = new Insets(0, 0, 7, 5);
		gbc_lblCertificateExpiration.gridx = 0;
		gbc_lblCertificateExpiration.gridy = 4;
		infoPanel.add(lblCertificateExpiration, gbc_lblCertificateExpiration);
		
		tfValidUntil = new JTextField();
		tfValidUntil.setEditable(false);
		GridBagConstraints gbc_tfValidUntil = new GridBagConstraints();
		gbc_tfValidUntil.insets = new Insets(0, 0, 7, 0);
		gbc_tfValidUntil.fill = GridBagConstraints.HORIZONTAL;
		gbc_tfValidUntil.gridx = 1;
		gbc_tfValidUntil.gridy = 4;
		infoPanel.add(tfValidUntil, gbc_tfValidUntil);
		tfValidUntil.setColumns(10);
		
		lblMembershipStatus = new JLabel("Membership Status:");
		GridBagConstraints gbc_lblMembershipStatus = new GridBagConstraints();
		gbc_lblMembershipStatus.anchor = GridBagConstraints.EAST;
		gbc_lblMembershipStatus.insets = new Insets(0, 0, 10, 5);
		gbc_lblMembershipStatus.gridx = 0;
		gbc_lblMembershipStatus.gridy = 5;
		infoPanel.add(lblMembershipStatus, gbc_lblMembershipStatus);
		
		tfMembershipStatus = new JTextField();
		tfMembershipStatus.setEditable(false);
		GridBagConstraints gbc_tfMembershipStatus = new GridBagConstraints();
		gbc_tfMembershipStatus.insets = new Insets(0, 0, 10, 0);
		gbc_tfMembershipStatus.fill = GridBagConstraints.HORIZONTAL;
		gbc_tfMembershipStatus.gridx = 1;
		gbc_tfMembershipStatus.gridy = 5;
		infoPanel.add(tfMembershipStatus, gbc_tfMembershipStatus);
		tfMembershipStatus.setColumns(10);
		
		lblPrivileges = new JLabel("Privileges:");
		GridBagConstraints gbc_lblPrivileges = new GridBagConstraints();
		gbc_lblPrivileges.anchor = GridBagConstraints.EAST;
		gbc_lblPrivileges.insets = new Insets(0, 0, 5, 5);
		gbc_lblPrivileges.gridx = 0;
		gbc_lblPrivileges.gridy = 6;
		infoPanel.add(lblPrivileges, gbc_lblPrivileges);
		
		taPrivileges = new JTextArea();
		taPrivileges.setEditable(false);
		taPrivileges.setWrapStyleWord(true);
		taPrivileges.setLineWrap(true);
		taPrivileges.setRows(2);
		GridBagConstraints gbc_taPrivileges= new GridBagConstraints();
		gbc_taPrivileges.insets = new Insets(0, 0, 5, 0);
		gbc_taPrivileges.fill = GridBagConstraints.BOTH;
		gbc_taPrivileges.gridx = 1;
		gbc_taPrivileges.gridy = 6;
		infoPanel.add(new JScrollPane(taPrivileges), gbc_taPrivileges);
		
		lblPublicSshKey = new JLabel("Public SSH Key:");
		GridBagConstraints gbc_lblPublicSshKey = new GridBagConstraints();
		gbc_lblPublicSshKey.anchor = GridBagConstraints.EAST;
		gbc_lblPublicSshKey.insets = new Insets(0, 0, 0, 5);
		gbc_lblPublicSshKey.gridx = 0;
		gbc_lblPublicSshKey.gridy = 7;
		infoPanel.add(lblPublicSshKey, gbc_lblPublicSshKey);
		
		taSshKey = new JTextArea();
		taSshKey.setEditable(false);
		taSshKey.setLineWrap(true);
		taSshKey.setRows(2);
		
		GridBagConstraints gbc_textArea = new GridBagConstraints();
		gbc_textArea.insets = new Insets(0, 0, 5, 0);
		gbc_textArea.fill = GridBagConstraints.BOTH;
		gbc_textArea.gridx = 1;
		gbc_textArea.gridy = 7;
		infoPanel.add(new JScrollPane(taSshKey), gbc_textArea);
		
		JSplitPane mid = new JSplitPane();		
		mid.setLeftComponent(scrollPane);
		mid.setRightComponent(panelRight);
		add(mid, BorderLayout.CENTER);
		
		splitPaneProjectSlices = new JSplitPane();
		panelRight.add(splitPaneProjectSlices, BorderLayout.CENTER);		
		
		listModelSlices = new SortedListModel<String>();
		listSlices= new JList(listModelSlices);	
		listSlices.setToolTipText("Double click an entry to see its details");
		listSlices.addMouseListener(new MouseAdapter() {
			@Override
			public void mouseClicked(MouseEvent e) {
				if(e.getClickCount() == 2)
				{
					mainGUI.setSelectedSlice((String)((JList)e.getSource()).getSelectedValue());
				}
			}
		});
		scrollPaneSlices = new JScrollPane(listSlices);
		scrollPaneSlices.setBorder(new TitledBorder("Member Slices"));
		splitPaneProjectSlices.setRightComponent(scrollPaneSlices);
		
		listModelProjects = new SortedListModel<String>();
		listProjects = new JList(listModelProjects);
		listProjects.setToolTipText("Double click an entry to see its details");
		listProjects.addMouseListener(new MouseAdapter() {
			@Override
			public void mouseClicked(MouseEvent e) {
				if(e.getClickCount() == 2)
				{
					mainGUI.setSelectedProject((String)((JList)e.getSource()).getSelectedValue());
				}
			}
		});
		scrollPaneProjects = new JScrollPane(listProjects);
		scrollPaneProjects.setBorder(new TitledBorder("Member Projects"));
		scrollPaneProjects.setPreferredSize(new Dimension(280,400));
		splitPaneProjectSlices.setLeftComponent(scrollPaneProjects);
		
		JPanel buttonPanel = new JPanel();
		buttonPanel.setLayout(new FlowLayout());
		buttonAddUser = new JButton("New Member");
		buttonPanel.add(buttonAddUser);
		buttonAddUser.addActionListener( new ActionListener(){
			@Override
			public void actionPerformed(ActionEvent arg0) {
								
				Member d = getMemberDetailInput(null);
				if( d != null)
				{
					Member rsp = MemberAuthorityAPI.addMember(d);
					if(rsp != null)
					{
						listModelMembers.add(rsp);
						saveCertificateAndKey(rsp, "Member has been added.");
						userList.setSelectedValue(rsp, true);
					}
					else
						showErrorMessage();
					
				}
			}			
		});
		buttonPanel.add(buttonRevokeUser);
		buttonPanel.add(buttonExtendMembership);
		buttonPanel.add(buttonEditUser);
		add(buttonPanel, BorderLayout.SOUTH);
		
		btnManagePrivileges = new JButton("Manage Privileges");
		btnManagePrivileges.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent arg0) {
				Member mem = (Member) userList.getSelectedValue();
				if(mem.username.equals("root") || mem.username.equals("expedient"))
				{
					JOptionPane.showMessageDialog(Members.this, mem.username+" is a privileged user. This membership cannot be modified.", "Assign Privileges", JOptionPane.INFORMATION_MESSAGE);
					return;                						
				}
				else
					showPrivilegesManagementDialog();
			}
		});
		buttonPanel.add(btnManagePrivileges);
		
		btnEditSshKey = new JButton("Edit SSH Key");
		btnEditSshKey.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent arg0) {
				Member mem = (Member) userList.getSelectedValue();
				JTextArea ta = new JTextArea(mem.pubSshKey);
				ta.setRows(5);
				ta.setColumns(40);
				ta.setLineWrap(true);
				Object[] choices;
				if(mem.pubSshKey != null && mem.pubSshKey.length()>0)
					choices = new String[]{"Update Key", "Delete Key", "Cancel"};
				else
					choices = new String[]{"Add Key", "Cancel"};
				int rv = JOptionPane.showOptionDialog(Members.this, new JScrollPane(ta), "Public SSH Key for "+mem.username, choices.length==2?JOptionPane.OK_CANCEL_OPTION:JOptionPane.YES_NO_CANCEL_OPTION, JOptionPane.PLAIN_MESSAGE, null, choices, choices[0]);
				if(rv == JOptionPane.NO_OPTION || ta.getText().trim().length() == 0) //Delete Key Option
				{
					if(mem.pubSshKey != null && mem.pubSshKey.length()>0)
					{
						Member rsp = MemberAuthorityAPI.deleteKey(mem);
						if(rsp == null)
							showErrorMessage();
						else
							taSshKey.setText("");
					}
				}
				else if(rv == JOptionPane.YES_OPTION || rv == JOptionPane.OK_OPTION) //Update key Option
				{
					//Return if nothing was edited
					if(ta.getText().trim().equals(mem.pubSshKey))
						return;
					
					Member rsp = null;
					
					if(mem.pubSshKey != null && mem.pubSshKey.length()>0) //Delete Existing Key
					{
						rsp = MemberAuthorityAPI.deleteKey(mem);
						if(rsp == null)
						{
							showErrorMessage();
							return;
						}
					}
					mem.pubSshKey = ta.getText().trim();
					rsp = MemberAuthorityAPI.addKey(mem);						
					if(rsp == null)
						showErrorMessage();
					else
					{
						taSshKey.setText(mem.pubSshKey);
						taSshKey.setToolTipText("KEY_ID:"+mem.pubSshKeyID);
					}
				}
			}
		});
		buttonPanel.add(btnEditSshKey);
		
		userList.addListSelectionListener( new ListSelectionListener() {

            @Override
            public void valueChanged(ListSelectionEvent arg0) {
                if (!arg0.getValueIsAdjusting()) {
  				  Member mem = (Member) userList.getSelectedValue();
                  
                  tfFirstName.setText(mem.fName+" "+mem.lName);
                  tfEmail.setText(mem.email);
                  //tfUsername.setText(memberDetails.get(index).username);
                  tfUserURN.setText(mem.urn);
                  //tfUserUUID.setText(memberDetails.get(index).uuid);                  
                  tfValidFrom.setText(Utils.formatDate(mem.cert.getNotBefore()));
                  tfValidUntil.setText(Utils.formatDate(mem.cert.getNotAfter()));
                  X509CRLEntry e = MemberAuthorityAPI.crl.getRevokedCertificate(mem.cert);
                  tfMembershipStatus.setText(e==null?"Active":"Revoked");
                  tfMembershipStatus.setForeground(e==null?DARK_GREEN:Color.RED);
                  taPrivileges.setText(Utils.join(mem.privileges));
                  taSshKey.setText(mem.pubSshKey);
                  taSshKey.setToolTipText("KEY_ID:"+mem.pubSshKeyID);
                  
                  LinkedList<AnObject> slices = SliceAuthorityAPI.lookupForMembers(mem.urn, "SLICE"); 
                  if(slices != null)
                  {
	                  listModelSlices.clear();
	                  for(int i=0; i<slices.size(); i++)
	                	  listModelSlices.add(slices.get(i).name);
                  }
                  else
                	  JOptionPane.showMessageDialog(Members.this, "Could not fetch member slices.", "Error", JOptionPane.ERROR_MESSAGE);;
                  
                  LinkedList<AnObject> projects = SliceAuthorityAPI.lookupForMembers(mem.urn, "PROJECT");                  
                  if(projects != null)
                  {
                	  listModelProjects.clear();
                	  for(int i=0; i<projects.size(); i++)
                		  listModelProjects.add(projects.get(i).name);
                  }
                  else
                	  JOptionPane.showMessageDialog(Members.this, "Could not fetch member projects.", "Error", JOptionPane.ERROR_MESSAGE);;

                }
            }
        }); 
		
		if(listModelMembers.getSize()>0)
			userList.setSelectedIndex(0);
		
		fileChooser = new JFileChooser();
		fileChooser.setFileSelectionMode(JFileChooser.DIRECTORIES_ONLY);
	
	}
	
	private void showErrorMessage()
	{
		JOptionPane.showMessageDialog(
			    this, 
			    "<html><body><p style='width: 300px;'>"+MemberAuthorityAPI.output+"</p></body></html>", 
			    "Error", 
			    JOptionPane.ERROR_MESSAGE);
	}
	
	private Member getMemberDetailInput(Member memDetails)
	{
		 
		JPanel infoPanel = new JPanel();
		infoPanel.setLayout(new GridBagLayout());
		
		GridBagConstraints c = new GridBagConstraints();
		c.fill = GridBagConstraints.HORIZONTAL;
		c.insets = new Insets(10,0,0,0);  //top padding
		c.weightx = 0.1;
		c.gridx = 0;
		c.gridy = 0;				
		infoPanel.add(new JLabel("First Name:"),c);
		c.gridy = 1;						
		infoPanel.add(new JLabel("Last Name:"),c);
		c.gridy = 2;						
		infoPanel.add(new JLabel("Email:"),c);
		
		JTextField tfFirstName, tfLastName, tfEmail, tfUsername;
		tfFirstName = new JTextField(memDetails==null?"":memDetails.fName);
		tfLastName = new JTextField(memDetails==null?"":memDetails.lName);
		tfEmail = new JTextField(memDetails==null?"":memDetails.email);	

		tfUsername = new JTextField(memDetails==null?"":memDetails.username);
	    ((AbstractDocument) tfUsername.getDocument()).setDocumentFilter(new PatternFilter("^[a-zA-Z][\\w]{0,7}"));
		
	    JCheckBox allowProjectCreation = new JCheckBox("Can create projects");
	    allowProjectCreation.setSelected(memDetails==null?true:memDetails.privileges.contains("PROJECT_CREATE"));
	    
		c.weightx = 0.9;
		c.gridx = 1;
		c.gridy = 0;		
		infoPanel.add(tfFirstName, c);
		c.gridy=1;		
		infoPanel.add(tfLastName, c);
		c.gridy=2;		
		infoPanel.add(tfEmail, c);
		
		if( memDetails==null ) 
		{
			c.gridy++;		
			infoPanel.add(tfUsername, c);
			c.weightx = 0.1;
			c.gridx = 0;						
			infoPanel.add(new JLabel("Username:"),c);			

			c.gridy++;
			c.gridx = 0;
			c.gridwidth=2;
			infoPanel.add(allowProjectCreation, c);
		}
		

		int response; 
		do{
			response = JOptionPane.showConfirmDialog(this, infoPanel,memDetails==null?"Add New Member":"Edit Member Details ",
	                JOptionPane.OK_CANCEL_OPTION, JOptionPane.PLAIN_MESSAGE);
			tfUsername.setBackground(tfUsername.getText().trim().length()==0?Color.pink:Color.white);
			tfFirstName.setBackground(tfFirstName.getText().trim().length()==0?Color.pink:Color.white);
			tfLastName.setBackground(tfLastName.getText().trim().length()==0?Color.pink:Color.white);
			tfEmail.setBackground(tfEmail.getText().trim().length()==0?Color.pink:Color.white);
		}
		while( (tfUsername.getText().length()==0  ||
			    tfFirstName.getText().length()==0 ||
			    tfLastName.getText().length()==0 ||
			    tfEmail.getText().length()==0) &&	
			   response == JOptionPane.OK_OPTION);
		
		if(response != JOptionPane.OK_OPTION)
			return null;
		else
		{
			Member d = new Member();
			d.fName = tfFirstName.getText().trim();
			d.lName = tfLastName.getText().trim();
			d.email = tfEmail.getText().trim();
			d.username = tfUsername.getText().trim();
			
			if(memDetails==null && allowProjectCreation.isSelected())
				d.privileges.add("PROJECT_CREATE");
			
			return d;
		}
	}
	
	private void saveCertificateAndKey(final Member md, String message)
	{
		Object[] options = {"Save"};
		final JOptionPane optionPane = new JOptionPane(message+"\nPlease save member certificate and key.", 
									 JOptionPane.INFORMATION_MESSAGE, JOptionPane.YES_OPTION, null, options, options[0]);
		
		final JDialog dialog = new JDialog();
		dialog.setTitle("Save Files");
		dialog.setContentPane(optionPane);
		dialog.setDefaultCloseOperation(JDialog.DO_NOTHING_ON_CLOSE);
		optionPane.addPropertyChangeListener(
			    new PropertyChangeListener() {
			        public void propertyChange(PropertyChangeEvent e) {
			            String prop = e.getPropertyName();

			            if (dialog.isVisible() 
			             && (e.getSource() == optionPane)
			             && (prop.equals(JOptionPane.VALUE_PROPERTY))) {
			                dialog.dispose();

			                int result = fileChooser.showSaveDialog(null);
			        		if (result == JFileChooser.APPROVE_OPTION) {
			        		    File dir = fileChooser.getSelectedFile();
			        		    try {
			        				PrintWriter out = new PrintWriter(new File(dir, md.username+"-cert.pem"));
			        				out.print(md.certStr);
			        				out.close();
			        				out = new PrintWriter(new File(dir, md.username+"-key.pem"));
			        				out.print(md.privateKey);			
			        				out.close();
			        			} catch (FileNotFoundException e1) {
			        				// TODO Auto-generated catch block
			        				e1.printStackTrace();
			        			}
			        		}
			            }
			        }
			    });		
		dialog.pack();
		dialog.setLocationRelativeTo(this);
		dialog.setVisible(true);
	}
	
	
	public Object[] getMemberArray()
	{
		return listModelMembers.toArray();
	}
	
	@SuppressWarnings("serial")
	private void showPrivilegesManagementDialog()
	{
		final String[] allPrivileges = { "PROJECT_CREATE"};
		Member member = (Member) userList.getSelectedValue();
		
		TransferHandler handler = new ListItemTransferHandler();
		DefaultListModel listModelAvailable = new DefaultListModel();
		for(int i=0; i<allPrivileges.length; i++)
			if(member.privileges.contains(allPrivileges[i]) == false)
				listModelAvailable.addElement(allPrivileges[i]);
		
        JList listAvailable = new JList(listModelAvailable);
        listAvailable.getSelectionModel().setSelectionMode(ListSelectionModel.MULTIPLE_INTERVAL_SELECTION);
        listAvailable.setDropMode(DropMode.INSERT);
        listAvailable.setDragEnabled(true);
        listAvailable.setTransferHandler(handler);
        JScrollPane splistAvailable = new JScrollPane(listAvailable);
        splistAvailable.setBorder(new TitledBorder("Unassigned Privileges"));
        listAvailable.setToolTipText("Use mouse to drag & drop elements between lists");
        

        //Disable row Cut, Copy, Paste
        ActionMap map = listAvailable.getActionMap();
        AbstractAction dummy = new AbstractAction() {
            @Override public void actionPerformed(ActionEvent e) { /* Dummy action */ }
        };
        map.put(TransferHandler.getCutAction().getValue(Action.NAME),   dummy);
        map.put(TransferHandler.getCopyAction().getValue(Action.NAME),  dummy);
        map.put(TransferHandler.getPasteAction().getValue(Action.NAME), dummy);

		DefaultListModel listModelAssigned = new DefaultListModel();
		for(int i=0; i<member.privileges.size(); i++)
			listModelAssigned.addElement(member.privileges.get(i));

		JList listAssigned = new JList(listModelAssigned);
        listAssigned.getSelectionModel().setSelectionMode(ListSelectionModel.MULTIPLE_INTERVAL_SELECTION);
        listAssigned.setDropMode(DropMode.INSERT);
        listAssigned.setDragEnabled(true);
        listAssigned.setTransferHandler(handler);
        JScrollPane splistAssigned = new JScrollPane(listAssigned);
        splistAssigned.setBorder(new TitledBorder("Assigned Privileges"));
        listAssigned.setToolTipText("Use mouse to drag & drop elements between lists");

        //Disable row Cut, Copy, Paste
        map = listAssigned.getActionMap();
        map.put(TransferHandler.getCutAction().getValue(Action.NAME),   dummy);
        map.put(TransferHandler.getCopyAction().getValue(Action.NAME),  dummy);
        map.put(TransferHandler.getPasteAction().getValue(Action.NAME), dummy);
        
        JPanel panel = new JPanel();
        panel.setLayout(new GridLayout(1,2,5,5));
        panel.add(splistAvailable);
        panel.add(splistAssigned);
        panel.setMinimumSize(new Dimension(500,200));
        panel.setPreferredSize(new Dimension(500,200));
        
		int response = JOptionPane.showConfirmDialog(this, panel, "Manage member privileges", JOptionPane.OK_CANCEL_OPTION, JOptionPane.PLAIN_MESSAGE);
		if(response == JOptionPane.OK_OPTION)
		{
			Object selectedPriveleges[] = listModelAssigned.toArray();

			if( Arrays.equals(selectedPriveleges, member.privileges.toArray()))
				return;
				
			Object res = MemberAuthorityAPI.assignPrivileges(member.urn, selectedPriveleges);
			if(res != null)
			{
				member.privileges.clear();
				for(int x=0; x<selectedPriveleges.length;x++)
					member.privileges.add((String) selectedPriveleges[x]);
				taPrivileges.setText(Utils.join(member.privileges));
			}
			else
				JOptionPane.showMessageDialog(Members.this, "Could not assign privileges.", "Error", JOptionPane.ERROR_MESSAGE);;
		}
		
	}
	
	public void refresh(Member[] memberData) {
		
		listModelMembers.clear();
		if(memberData != null)
			listModelMembers.addAll(memberData);
		userList.setSelectedIndex(0);
		
	}
}


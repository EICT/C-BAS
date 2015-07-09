package admin.cbas.eict.de;

import javax.swing.JPanel;

import java.awt.BorderLayout;

import javax.swing.JScrollPane;
import javax.swing.ListSelectionModel;
import javax.swing.JLabel;
import javax.swing.RowFilter;

import admin.cbas.eict.de.LoggingAuthorityAPI.LogEvent;
import admin.cbas.eict.de.MemberAuthorityAPI.Member;

import java.awt.Component;
import java.awt.FlowLayout;
import java.text.SimpleDateFormat;
import java.util.Arrays;
import java.util.Date;
import java.util.GregorianCalendar;

import javax.swing.JComboBox;
import javax.swing.JCheckBox;
import javax.swing.DefaultComboBoxModel;

import java.awt.event.ActionListener;
import java.awt.event.ActionEvent;
import java.awt.GridLayout;

import javax.swing.JButton;
import javax.swing.SwingConstants;
import javax.swing.Box;
import javax.swing.border.TitledBorder;
import javax.swing.table.TableModel;
import javax.swing.table.TableRowSorter;

public class Logs extends JPanel {
	/**ad
	 * 
	 */
	private static final long serialVersionUID = -230633782772635859L;
	private ColoredJTable table;
	CustomTableModel tableModel;
	DateTimePicker datePanelFrom, datePanelTo;
	JComboBox comboBoxSub;
	JComboBox comboBoxObjType;
	JComboBox comboBoxObjURN, comboBoxAct;
	SimpleDateFormat timeFormatPicker = new SimpleDateFormat("HH:mm:ss");
	SimpleDateFormat dateFormatTimestamp = new SimpleDateFormat("yyyy-MM-dd    HH:mm:ss.SSS");
	TableRowSorter<TableModel> tableSorter;
	String[] readableActions, cbasActions;
	MainGUI mainGUI;
	JCheckBox chckbxDate;
	
	/**
	 * Create the panel.
	 */
	public Logs(MainGUI parent, LogEvent[] logs) {
		
		mainGUI = parent;
		setLayout(new BorderLayout(0, 0));
		
		JPanel filterPanel = new JPanel();
		filterPanel.setBorder(new TitledBorder("Filters"));
		add(filterPanel, BorderLayout.NORTH);
		filterPanel.setLayout(new GridLayout(5, 1, 0, 0));
		
		JPanel panelDateFilter = new JPanel();
		FlowLayout fl_panelDateFilter = (FlowLayout) panelDateFilter.getLayout();
		fl_panelDateFilter.setAlignment(FlowLayout.LEFT);
		filterPanel.add(panelDateFilter);
        
        chckbxDate = new JCheckBox("Date:");
        panelDateFilter.add(chckbxDate);
        chckbxDate.addActionListener(new ActionListener() {
        	public void actionPerformed(ActionEvent e) {
        		JCheckBox cb = (JCheckBox)e.getSource();
        		datePanelFrom.setEnabled(cb.isSelected());
        		datePanelTo.setEnabled(cb.isSelected());
        		
        		if(cb.isSelected())
        		{
        			
        		}
        	}
        });
		
        datePanelFrom = new DateTimePicker();
        datePanelFrom.setEnabled(false);
        datePanelFrom.setFormats( dateFormatTimestamp);
        datePanelFrom.setTimeFormat( timeFormatPicker );
		panelDateFilter.add((Component) datePanelFrom);
		datePanelFrom.getEditor().setEditable(false);
		
		JLabel lblTo = new JLabel("to");
		panelDateFilter.add(lblTo);
		
        datePanelTo = new DateTimePicker();
        datePanelTo.setEnabled(false);
        datePanelTo.setFormats( dateFormatTimestamp );
        datePanelTo.setTimeFormat( timeFormatPicker);
		panelDateFilter.add((Component) datePanelTo);
		datePanelTo.getEditor().setEditable(false);
		
		JPanel panelObjFilter = new JPanel();
		FlowLayout fl_panelObjFilter = (FlowLayout) panelObjFilter.getLayout();
		fl_panelObjFilter.setAlignment(FlowLayout.LEFT);
		filterPanel.add(panelObjFilter);
		
		JCheckBox chbxObjType = new JCheckBox("Object Type:");
		chbxObjType.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e) {
				JCheckBox cb = (JCheckBox)e.getSource();
				comboBoxObjType.setEnabled(cb.isSelected());
			}
		});
		panelObjFilter.add(chbxObjType);
		
		comboBoxObjType = new JComboBox();
		comboBoxObjType.setEnabled(false);
		comboBoxObjType.setModel(new DefaultComboBoxModel(new String[] {"Slice", "Project", "User", "Key"}));
		panelObjFilter.add(comboBoxObjType);
		
		Component horizontalStrut = Box.createHorizontalStrut(20);
		panelObjFilter.add(horizontalStrut);
		
		JCheckBox chbxUrn = new JCheckBox("Object URN:");
		chbxUrn.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e) {
				JCheckBox cb = (JCheckBox)e.getSource();
				comboBoxObjURN.setEnabled(cb.isSelected());
			}
		});
		panelObjFilter.add(chbxUrn);
		
		comboBoxObjURN = new JComboBox();
		comboBoxObjURN.setEnabled(false);
		panelObjFilter.add(comboBoxObjURN);
		
		JPanel panelSubFilter = new JPanel();
		FlowLayout flowLayout_1 = (FlowLayout) panelSubFilter.getLayout();
		flowLayout_1.setAlignment(FlowLayout.LEFT);
		filterPanel.add(panelSubFilter);
		
		JCheckBox chckbxSubject = new JCheckBox("Subject:");
		chckbxSubject.setHorizontalAlignment(SwingConstants.LEFT);
		panelSubFilter.add(chckbxSubject);
		
		comboBoxSub = new JComboBox();
		comboBoxSub.setEnabled(false);
		panelSubFilter.add(comboBoxSub);
		
		JPanel panelActFilter = new JPanel();
		FlowLayout flowLayout_2 = (FlowLayout) panelActFilter.getLayout();
		flowLayout_2.setAlignment(FlowLayout.LEFT);
		filterPanel.add(panelActFilter);
		
		JCheckBox chckbxAct = new JCheckBox("Action:");
		chckbxAct.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e) {
				JCheckBox cb = (JCheckBox)e.getSource();
				comboBoxAct.setEnabled(cb.isSelected());
			}
		});
		panelActFilter.add(chckbxAct);
		
		comboBoxAct = new JComboBox();
		comboBoxAct.setEnabled(false);
		panelActFilter.add(comboBoxAct);
		
		readableActions = new String[] {"Create", "Update", "Delete", "Modify slice/project membership", "Revoke certificate", "Renew membership"};
		cbasActions = new String[] {"create", "update", "delete", "modify_membership", "Revoke certificate", "Renew"};
		comboBoxAct.setModel(new DefaultComboBoxModel(readableActions));
		
		JPanel panelReload = new JPanel();
		FlowLayout flowLayout = (FlowLayout) panelReload.getLayout();
		flowLayout.setAlignment(FlowLayout.LEFT);
		filterPanel.add(panelReload);
		
		JButton btnReload = new JButton("Apply");
		btnReload.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent arg0) {
				setFilter();
			}
		});
		panelReload.add(btnReload);
		chckbxSubject.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e) {
				JCheckBox cb = (JCheckBox)e.getSource();
				comboBoxSub.setEnabled(cb.isSelected());
				if(cb.isSelected() == true)
				{
					Object[] members = mainGUI.getMembersArray();
					comboBoxSub.setModel(new DefaultComboBoxModel(members));
				}
			}
		});
		
		JScrollPane scrollPane = new JScrollPane();
		add(scrollPane, BorderLayout.CENTER);
		
		String headers[] =  new String[]{"Timestamp", "Subject", "Object", "Action", "Parameters"};				
		Arrays.sort(logs);
		String[][] data = new String[logs.length][headers.length];
		for(int x=0; x<logs.length; x++)
			data[x] = logs[x].getEntry(dateFormatTimestamp);
		
		tableModel = new CustomTableModel(data,headers);		
		table = new ColoredJTable(tableModel);
		tableSorter = new TableRowSorter<TableModel>(table.getModel());
		table.setRowSorter(tableSorter);
		table.setSelectionMode(ListSelectionModel.SINGLE_SELECTION);
		table.getColumnModel().getColumn(1).setPreferredWidth(75);
		table.getColumnModel().getColumn(1).setMaxWidth(75);
		JScrollPane memberScrollPane = new JScrollPane(table);
		add(memberScrollPane, BorderLayout.CENTER);
		setFilter();
	}
	
	private void setFilter()
	{
		 RowFilter<TableModel,Integer> filter = new RowFilter<TableModel,Integer>() {
			   
			 public boolean include(Entry<? extends TableModel, ? extends Integer> entry) {
				 TableModel model = entry.getModel();
				 int row = entry.getIdentifier();
				 
				 //Filter Object Type
				 if(comboBoxObjType.isEnabled())
				 {
					 String objTypeToFilter = (String) comboBoxObjType.getSelectedItem();
					 String obj = (String) model.getValueAt(row, 2);
					 if(!obj.startsWith(objTypeToFilter.toLowerCase()))
						 return false;
				 }

				 //Filter Action
				 if(comboBoxAct.isEnabled())
				 {
					 String actionToFilter = cbasActions[comboBoxAct.getSelectedIndex()];
					 String action = (String) model.getValueAt(row, 3);
					 if(!action.equalsIgnoreCase(actionToFilter))
						 return false;
				 }

				 //Filter Subject
				 if(comboBoxSub.isEnabled())
				 {
					 String subToFilter = ((Member)comboBoxSub.getSelectedItem()).toString();
					 String sub = (String) model.getValueAt(row, 1);
					 if(!sub.equalsIgnoreCase(subToFilter))
						 return false;
				 }

				 //Filter Date
				 if(chckbxDate.isSelected())
				 {
					 String timestamp = (String) model.getValueAt(row, 0);
					 String from = datePanelFrom.getEditor().getText();
					 String to = datePanelTo.getEditor().getText();
					 
					 if(from == null || from.length()==0)
						 from = dateFormatTimestamp.format(new Date(0));
					 
					 if(to == null || to.length()==0)
						 to = dateFormatTimestamp.format(new GregorianCalendar(2100, 1, 1).getTime());
					 
					 if(timestamp.compareTo(from) < 0 || timestamp.compareTo(to) > 0)
						 return false;
				 }
				 
			     return true;
			   }
			 };
		tableSorter.setRowFilter(filter);
	}
}

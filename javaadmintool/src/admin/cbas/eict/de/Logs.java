package admin.cbas.eict.de;

import javax.swing.JPanel;

import java.awt.BorderLayout;
import javax.swing.JScrollPane;
import javax.swing.ListSelectionModel;
import javax.swing.JLabel;
import admin.cbas.eict.de.LoggingAuthorityAPI.LogEvent;
import java.awt.Component;
import java.awt.FlowLayout;
import java.text.SimpleDateFormat;
import java.util.Arrays;
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
	SimpleDateFormat dateFormatPicker = new SimpleDateFormat("dd-MM-yyyy HH:mm:ss");
	SimpleDateFormat timeFormatPicker = new SimpleDateFormat("HH:mm:ss");
	SimpleDateFormat dateFormatTimestamp = new SimpleDateFormat("yyyy-MM-dd    HH:mm:ss.SSS");
	
	/**
	 * Create the panel.
	 */
	public Logs(MainGUI parent, LogEvent[] logs) {
		setLayout(new BorderLayout(0, 0));
		
		JPanel filterPanel = new JPanel();
		filterPanel.setBorder(new TitledBorder("Filters"));
		add(filterPanel, BorderLayout.NORTH);
		filterPanel.setLayout(new GridLayout(5, 1, 0, 0));
		
		JPanel panelDateFilter = new JPanel();
		FlowLayout fl_panelDateFilter = (FlowLayout) panelDateFilter.getLayout();
		fl_panelDateFilter.setAlignment(FlowLayout.LEFT);
		filterPanel.add(panelDateFilter);
        
        JCheckBox chckbxDate = new JCheckBox("Date:");
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
        datePanelFrom.setFormats( dateFormatPicker);
        datePanelFrom.setTimeFormat( timeFormatPicker );
		panelDateFilter.add((Component) datePanelFrom);
				
		JLabel lblTo = new JLabel("to");
		panelDateFilter.add(lblTo);
		
        datePanelTo = new DateTimePicker();
        datePanelTo.setEnabled(false);
        datePanelTo.setFormats( dateFormatPicker );
        datePanelTo.setTimeFormat( timeFormatPicker);
		panelDateFilter.add((Component) datePanelTo);
		
		JPanel panelObjFilter = new JPanel();
		FlowLayout fl_panelObjFilter = (FlowLayout) panelObjFilter.getLayout();
		fl_panelObjFilter.setAlignment(FlowLayout.LEFT);
		filterPanel.add(panelObjFilter);
		
		JCheckBox chbxType = new JCheckBox("Object Type:");
		chbxType.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e) {
				JCheckBox cb = (JCheckBox)e.getSource();
				comboBoxObjType.setEnabled(cb.isSelected());
			}
		});
		panelObjFilter.add(chbxType);
		
		comboBoxObjType = new JComboBox();
		comboBoxObjType.setEnabled(false);
		comboBoxObjType.setModel(new DefaultComboBoxModel(new String[] {"Slice", "Project", "Member", "Key"}));
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
		comboBoxAct.setModel(new DefaultComboBoxModel(new String[] {"Create", "Update", "Delete", "Modify membership for slice/project", "Revoke certificate"}));
		
		JPanel panelReload = new JPanel();
		FlowLayout flowLayout = (FlowLayout) panelReload.getLayout();
		flowLayout.setAlignment(FlowLayout.LEFT);
		filterPanel.add(panelReload);
		
		JButton btnReload = new JButton("Apply");
		panelReload.add(btnReload);
		chckbxSubject.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e) {
				JCheckBox cb = (JCheckBox)e.getSource();
				comboBoxSub.setEnabled(cb.isSelected());
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
		table.setSelectionMode(ListSelectionModel.SINGLE_SELECTION);
		table.getColumnModel().getColumn(1).setPreferredWidth(75);
		table.getColumnModel().getColumn(1).setMaxWidth(75);
		JScrollPane memberScrollPane = new JScrollPane(table);
		add(memberScrollPane, BorderLayout.CENTER);

	}
}

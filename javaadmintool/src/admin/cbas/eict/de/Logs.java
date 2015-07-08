package admin.cbas.eict.de;

import javax.swing.JPanel;

import java.awt.BorderLayout;

import javax.swing.JFrame;
import javax.swing.JScrollPane;
import javax.swing.JTable;
import javax.swing.ListSelectionModel;

import java.awt.GridBagLayout;

import javax.swing.JLabel;

import admin.cbas.eict.de.LoggingAuthorityAPI.LogEvent;

import java.awt.Component;
import java.awt.GridBagConstraints;
import java.awt.Insets;
import java.awt.FlowLayout;
import java.text.DateFormat;
import javax.swing.JComboBox;
import javax.swing.JCheckBox;

public class Logs extends JPanel {
	/**ad
	 * 
	 */
	private static final long serialVersionUID = -230633782772635859L;
	private JTable table;
	MemberTableModel tableModel; 

	/**
	 * Create the panel.
	 */
	public Logs() {
		setLayout(new BorderLayout(0, 0));
		
		JPanel filterPanel = new JPanel();
		add(filterPanel, BorderLayout.NORTH);
		GridBagLayout gbl_filterPanel = new GridBagLayout();
		gbl_filterPanel.columnWidths = new int[]{0, 0, 0, 0, 0, 0};
		gbl_filterPanel.rowHeights = new int[]{0, 0, 0};
		gbl_filterPanel.columnWeights = new double[]{0.0, 1.0, 0.0, 1.0, 1.0, Double.MIN_VALUE};
		gbl_filterPanel.rowWeights = new double[]{1.0, Double.MIN_VALUE, 0.0};
		filterPanel.setLayout(gbl_filterPanel);
		
		JCheckBox chckbxDate = new JCheckBox("Date:");
		GridBagConstraints gbc_chckbxDate = new GridBagConstraints();
		gbc_chckbxDate.anchor = GridBagConstraints.WEST;
		gbc_chckbxDate.insets = new Insets(0, 0, 5, 5);
		gbc_chckbxDate.gridx = 0;
		gbc_chckbxDate.gridy = 0;
		filterPanel.add(chckbxDate, gbc_chckbxDate);
		
		JCheckBox chckbxSubject = new JCheckBox("Subject:");
		GridBagConstraints gbc_chckbxSubject = new GridBagConstraints();
		gbc_chckbxSubject.anchor = GridBagConstraints.WEST;
		gbc_chckbxSubject.insets = new Insets(0, 0, 5, 5);
		gbc_chckbxSubject.gridx = 0;
		gbc_chckbxSubject.gridy = 1;
		filterPanel.add(chckbxSubject, gbc_chckbxSubject);
		
		JPanel panel = new JPanel();
		FlowLayout flowLayout = (FlowLayout) panel.getLayout();
		flowLayout.setAlignment(FlowLayout.LEFT);
		GridBagConstraints gbc_panel = new GridBagConstraints();
		gbc_panel.insets = new Insets(0, 0, 5, 5);
		gbc_panel.fill = GridBagConstraints.BOTH;
		gbc_panel.gridx = 1;
		gbc_panel.gridy = 0;
		filterPanel.add(panel, gbc_panel);
		
		
        DateTimePicker datePanelFrom = new DateTimePicker();
        datePanelFrom.setFormats( DateFormat.getDateTimeInstance( DateFormat.SHORT, DateFormat.MEDIUM ) );
        datePanelFrom.setTimeFormat( DateFormat.getTimeInstance( DateFormat.MEDIUM ) );
		panel.add((Component) datePanelFrom);
				
		JLabel lblTo = new JLabel("to");
		panel.add(lblTo);
		
        DateTimePicker datePanelTo = new DateTimePicker();
		panel.add((Component) datePanelTo);
		
		JComboBox comboBox_1 = new JComboBox();
		GridBagConstraints gbc_comboBox_1 = new GridBagConstraints();
		gbc_comboBox_1.insets = new Insets(0, 0, 5, 5);
		gbc_comboBox_1.fill = GridBagConstraints.HORIZONTAL;
		gbc_comboBox_1.gridx = 1;
		gbc_comboBox_1.gridy = 2;
		filterPanel.add(comboBox_1, gbc_comboBox_1);
		
		JCheckBox chckbxObject = new JCheckBox("Object Type:");
		GridBagConstraints gbc_chckbxObject = new GridBagConstraints();
		gbc_chckbxObject.anchor = GridBagConstraints.WEST;
		gbc_chckbxObject.insets = new Insets(0, 0, 5, 5);
		gbc_chckbxObject.gridx = 0;
		gbc_chckbxObject.gridy = 2;
		filterPanel.add(chckbxObject, gbc_chckbxObject);
		
		JComboBox comboBox = new JComboBox();
		GridBagConstraints gbc_comboBox = new GridBagConstraints();
		gbc_comboBox.insets = new Insets(0, 0, 5, 5);
		gbc_comboBox.fill = GridBagConstraints.HORIZONTAL;
		gbc_comboBox.gridx = 1;
		gbc_comboBox.gridy = 1;
		filterPanel.add(comboBox, gbc_comboBox);
		
		JCheckBox chckbxMethod = new JCheckBox("Action:");
		GridBagConstraints gbc_chckbxMethod = new GridBagConstraints();
		gbc_chckbxMethod.anchor = GridBagConstraints.WEST;
		gbc_chckbxMethod.insets = new Insets(0, 0, 0, 5);
		gbc_chckbxMethod.gridx = 0;
		gbc_chckbxMethod.gridy = 3;
		filterPanel.add(chckbxMethod, gbc_chckbxMethod);
		
		JComboBox comboBox_2 = new JComboBox();
		GridBagConstraints gbc_comboBox_2 = new GridBagConstraints();
		gbc_comboBox_2.insets = new Insets(0, 0, 0, 5);
		gbc_comboBox_2.fill = GridBagConstraints.HORIZONTAL;
		gbc_comboBox_2.gridx = 1;
		gbc_comboBox_2.gridy = 3;
		filterPanel.add(comboBox_2, gbc_comboBox_2);
		
		JScrollPane scrollPane = new JScrollPane();
		add(scrollPane, BorderLayout.CENTER);
				
		LogEvent e[] = LoggingAuthorityAPI.lookupAll();
		String[][] data = new String[e.length][4];
		for(int x=0; x<e.length; x++)
			data[x] = e[x].getEntry();
		
		tableModel = new MemberTableModel(data, new String[]{"Timestamp", "Subject", "Object", "Action"});		
		table = new JTable(tableModel);
		table.setSelectionMode(ListSelectionModel.SINGLE_SELECTION);
//		table.getColumnModel().getColumn(0).setPreferredWidth(300);
//		table.getColumnModel().getColumn(1).setPreferredWidth(75);
//		table.getColumnModel().getColumn(1).setMaxWidth(75);
		JScrollPane memberScrollPane = new JScrollPane(table);
//		memberScrollPane.setToolTipText("Double click an entry to see its details");
		add(memberScrollPane, BorderLayout.CENTER);
		

	}
	
	public static void main(String args[]) throws Exception
	{
		
		
		
		JFrame f = new JFrame("Logs");
		f.getContentPane().add(new Logs());
		f.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		f.pack();f.setVisible(true);
	}
	
}

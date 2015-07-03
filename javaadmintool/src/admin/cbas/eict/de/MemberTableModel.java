package admin.cbas.eict.de;

import java.util.ArrayList;

import javax.swing.table.AbstractTableModel;

//class that extends the AbstractTableModel
public class MemberTableModel extends AbstractTableModel {

	/**
	 * 
	 */
	private static final long serialVersionUID = 5213220199876788215L;
	//data
	ArrayList<String[]> al;
	// the headers
	String[] header;
	
	// constructor 
	MemberTableModel(String[][] obj, String[] header) {
		// save the header
		this.header = header;	
		// and the rows
		al = new ArrayList<String[]>();
		
		// copy the rows into the ArrayList
		if(obj != null)
		{
			for(int i = 0; i < obj.length; ++i)
				al.add(obj[i]);
		}
	}
	// method that needs to be overload. The row count is the size of the ArrayList
	public int getRowCount() {
		return al.size();
	}

	// method that needs to be overload. The column count is the size of our header
	public int getColumnCount() {
		return header.length;
	}

	// method that needs to be overload. The object is in the arrayList at rowIndex
	public Object getValueAt(int rowIndex, int columnIndex) {
		return al.get(rowIndex)[columnIndex];
	}
	
	// a method to return the column name 
	public String getColumnName(int index) {
		return header[index];
	}
	
	// a method to add a new line to the table
	void add(String member, String role) {
		al.add(new String[]{member, role});
		// inform the GUI that I have change
		fireTableDataChanged();
	}
	
	void clear(){
		al.clear();
		fireTableDataChanged();
	}
	
	void remove(int row){
		al.remove(row);
		fireTableDataChanged();
	}
	
	public void setValueAt(Object value, int row, int col)
	{
		al.get(row)[col] = (String)value;		
		fireTableCellUpdated(row, col);
	}
	
}

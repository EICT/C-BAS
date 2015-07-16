package admin.cbas.eict.de;

import java.awt.datatransfer.*;
import javax.activation.*;
import javax.swing.*;

//
public class ListItemTransferHandler extends TransferHandler {
  /**
	 * Demo - BasicDnD (Drag and Drop and Data Transfer)>http://docs.oracle.com/javase/tutorial/uiswing/dnd/basicdemo.html 
	 */
	private static final long serialVersionUID = -2472921998658718329L;
	private final DataFlavor localObjectFlavor;
	private JList source;
	private int[] indices;
	private int addIndex = -1; //Location where items were added
	private int addCount; //Number of items added.

  public ListItemTransferHandler() {
      super();
      localObjectFlavor = new ActivationDataFlavor(Object[].class, DataFlavor.javaJVMLocalObjectMimeType, "Array of items");
  }
  @Override protected Transferable createTransferable(JComponent c) {
      source = (JList) c;
      indices = source.getSelectedIndices();
      Object[] transferedObjects = source.getSelectedValues();
      return new DataHandler(transferedObjects, localObjectFlavor.getMimeType());
  }
  @Override public boolean canImport(TransferSupport info) {
      return info.isDrop() && info.isDataFlavorSupported(localObjectFlavor);
  }
  @Override public int getSourceActions(JComponent c) {
      return MOVE; //TransferHandler.COPY_OR_MOVE;
  }
  
  @Override public boolean importData(TransferSupport info) {
      if (!canImport(info)) {
          return false;
      }
      TransferHandler.DropLocation tdl = info.getDropLocation();
      if (!(tdl instanceof JList.DropLocation)) {
          return false;
      }
      JList.DropLocation dl = (JList.DropLocation) tdl;
      JList target = (JList) info.getComponent();
      DefaultListModel listModel = (DefaultListModel) target.getModel();
      int index = dl.getIndex();
      //boolean insert = dl.isInsert();
      int max = listModel.getSize();
      if (index < 0 || index > max) {
          index = max;
      }
      addIndex = index;

      try {
          Object[] values = (Object[]) info.getTransferable().getTransferData(localObjectFlavor);
          for (int i = 0; i < values.length; i++) {
              int idx = index++;
              listModel.add(idx, values[i]);
              target.addSelectionInterval(idx, idx);
          }
          addCount = target.equals(source) ? values.length : 0;
          return true;
      } catch (Exception ex) {
          ex.printStackTrace();
      }
      return false;
  }
  @Override protected void exportDone(JComponent c, Transferable data, int action) {
      cleanup(c, action == MOVE);
  }
  private void cleanup(JComponent c, boolean remove) {
      if (remove && indices != null) {
          //If we are moving items around in the same list, we
          //need to adjust the indices accordingly, since those
          //after the insertion point have moved.
          if (addCount > 0) {
              for (int i = 0; i < indices.length; i++) {
                  if (indices[i] >= addIndex) {
                      indices[i] += addCount;
                  }
              }
          }
          JList source = (JList) c;
          DefaultListModel model  = (DefaultListModel) source.getModel();
          for (int i = indices.length - 1; i >= 0; i--) {
              model.remove(indices[i]);
          }
      }
      indices  = null;
      addCount = 0;
      addIndex = -1;
  }
}
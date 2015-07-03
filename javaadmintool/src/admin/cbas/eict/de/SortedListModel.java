package admin.cbas.eict.de;

import java.util.Arrays;
import java.util.Collection;
import java.util.Iterator;
import java.util.SortedSet;
import java.util.TreeSet;

import javax.swing.AbstractListModel;

public class SortedListModel<E> extends AbstractListModel{

		  /**
	 * 
	 */
	private static final long serialVersionUID = 8586458811142495228L;
		SortedSet<E> model;

		  public SortedListModel() {
		    model = new TreeSet<E>();
		  }

		  public int getSize() {
		    return model.size();
		  }

		  @SuppressWarnings("unchecked")
		public E getElementAt(int index) {
		    return (E) model.toArray()[index];
		  }
		  
		public E get(int index)
		{
			return getElementAt(index);
		}

		  public void add(E element) {
		    if (model.add(element)) {
		      fireContentsChanged(this, 0, getSize());
		    }
		  }

		  public void addAll(E elements[]) {
		    Collection<E> c = Arrays.asList(elements);
		    model.addAll(c);
		    fireContentsChanged(this, 0, getSize());
		  }

		  public void clear() {
		    model.clear();
		    fireContentsChanged(this, 0, getSize());
		  }

		  public boolean contains(E element) {
		    return model.contains(element);
		  }

		  public E firstElement() {
		    return model.first();
		  }

		  public Iterator<E> iterator() {
		    return model.iterator();
		  }

		  public Object lastElement() {
		    return model.last();
		  }

		  public boolean removeElement(E element) {
		    boolean removed = model.remove(element);
		    if (removed) {
		      fireContentsChanged(this, 0, getSize());
		    }
		    return removed;
		  }
		
		  
		public Object[] toArray()
		  {
			  return model.toArray();
		  }
	
}

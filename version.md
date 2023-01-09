##### **V2.1.1**
<table>
    <tr><th>Type</th><th>Module</th><th>Description</th></tr>
    <tr><td>New</td><td>GRN</td>
        <td>
            A GRN ( Good Receive Note ) to acknowledge purchase received
            <ol>
                <li>Cannot make direct GRN, all GRN should have a purchase order</li>
                <li>All GRN documents require an invoice number</li>
                <li>On approval, GRN should adjust stock</li>
            </ol>
        </td>
    </tr>
    <tr>
        <td>Update</td>
        <td>PO</td>
        <td>
            <ol>
                <li>Enable approval on purchasing</li>
                <li>Make transaction packing relational to ProductsPacking</li>
                <li>When a transaction is being saved, it also consider the current pack quantity aside the relation</li>
                <li>Save tran quantity at the time of making PO Document so future changes wont affect any data</li>
            </ol>
        </td>
    </tr>
    <tr>
        <td>UPDATE</td>
        <td>Meeting</td>
        <td>Setting open meeting url same as config</td>
    </tr>
    <tr>
        <td>UPDATE</td>
        <td>Meeting</td>
        <td>Effective close meeting button</td>
    </tr>
</table>
import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;

class UserRepository {
  ResultSet find(Connection db, String userId) throws SQLException {
    var statement = db.prepareStatement("SELECT * FROM users WHERE id = ?");
    var normalizedId = userId.trim().toLowerCase();
    statement.setString(1, normalizedId);
    return statement.executeQuery();
  }
}

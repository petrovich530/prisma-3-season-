package prisma.prismacoin;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import net.fabricmc.api.ModInitializer;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.network.ServerPlayerEntity;
import net.minecraft.util.Util;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;

public class Prismacoin implements ModInitializer {
    private static final String DATABASE_URL = "jdbc:sqlite:player_times.sqlite";

    @Override
    public void onInitialize() {
        createTableIfNotExists();

        ServerTickEvents.END_SERVER_TICK.register(server -> {
            server.getPlayerManager().getPlayerList().forEach(this::trackPlayerTime);
        });
    }

    private void createTableIfNotExists() {
        try (Connection conn = DriverManager.getConnection(DATABASE_URL);
             PreparedStatement stmt = conn.prepareStatement(
                     "CREATE TABLE IF NOT EXISTS player_times (" +
                             "  uuid TEXT PRIMARY KEY," +
                             "  name TEXT," +
                             "  total_time INTEGER" +
                             ")"
             )) {
            stmt.executeUpdate();
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }

    private void trackPlayerTime(ServerPlayerEntity player) {
        new Thread(() -> {
            try (Connection conn = DriverManager.getConnection(DATABASE_URL);
                 PreparedStatement stmtSelect = conn.prepareStatement("SELECT total_time FROM player_times WHERE uuid = ?");
                 PreparedStatement stmtInsert = conn.prepareStatement("INSERT OR REPLACE INTO player_times (uuid, name, total_time) VALUES (?, ?, ?)");
                 PreparedStatement stmtUpdate = conn.prepareStatement("UPDATE player_times SET total_time = ? WHERE uuid = ?")) {

                stmtSelect.setString(1, player.getUuidAsString());
                ResultSet rs = stmtSelect.executeQuery();
                int totalTime = 0; // Предполагаем, что данные не найдены и устанавливаем totalTime в 0

                if (rs.next()) {
                    totalTime = rs.getInt("total_time");
                }
                rs.close();

                while (true) {
                    Thread.sleep(60000); // Track time every minute
                    totalTime += 1;

                    // Обновление или вставка данных в таблицу
                    stmtUpdate.setInt(1, totalTime);
                    stmtUpdate.setString(2, player.getUuidAsString());
                    int rowsUpdated = stmtUpdate.executeUpdate();

                    if (rowsUpdated == 0) {
                        // Если ни одна запись не была обновлена (значит, запись для этого игрока отсутствует), вставляем новую запись
                        stmtInsert.setString(1, player.getUuidAsString());
                        stmtInsert.setString(2, player.getName().toString().replaceAll("[^a-zA-Za-яА-я ]", ""));
                        stmtInsert.setInt(3, totalTime);
                        stmtInsert.executeUpdate();
                    }
                }
            } catch (SQLException | InterruptedException e) {
                e.printStackTrace();
            }
        }).start();
    }
}


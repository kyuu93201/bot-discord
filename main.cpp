#include <iostream>
#include <cstring>
#include <windows.h>
#include <cstdlib>   
#include <ctime>     
#include <vector>    
#include <fstream>   // Thư viện để ghi file văn bản cho Bot đọc
#include <discord_rpc.h>

const char* APPLICATION_ID = "id-may-khach";

struct RandomMessage {
    std::string text;
    std::string emoji;
};

// Danh sách lời nhắn và ID Emoji từ ảnh image_fd747f.png
std::vector<RandomMessage> msgList = {
    {"Vừa bay vào sảnh chờ xong!", "<:nE:1484203703811702967>"},
    {"Chào anh em nhé, chiến thôi!", "<:download:1484203701282537632>"},
    {"Ủa phòng này full chưa vậy?", "<:download2:1484203699101368562>"},
    {"Sẵn sàng bấm Ready đi kìa!", "<:download1:1484203696123543723>"},
    {"Hello, cho xin một slot chơi cùng với!", "<:aihi_:1484203693661225001>"},
    {"Game này dễ, để tôi gánh cho!", "<:meme:1484203691576655952>"}
};

static void UpdatePresence()
{
    DiscordRichPresence discordPresence;
    memset(&discordPresence, 0, sizeof(discordPresence));
    discordPresence.state = "Playing Solo";
    discordPresence.details = "Competitive";
    discordPresence.startTimestamp = 1507665886;
    discordPresence.endTimestamp = 1507665886;
    discordPresence.largeImageText = "Numbani";
    discordPresence.smallImageText = "Rogue - Level 100";
    discordPresence.partyId = "ae488379-351d-4a4f-ad32-2b9b01c91657";
    discordPresence.partySize = 1;
    discordPresence.partyMax = 5;
    discordPresence.joinSecret = "MTI4NzM0OjFpMmhuZToxMjMxMjM= ";
    Discord_UpdatePresence(&discordPresence);
}

void handleDiscordReady(const DiscordUser* connectedUser) {
    std::cout << "[+] Discord Ready! Connected to user: " << connectedUser->username << std::endl;
}

void handleDiscordDisconnected(int errcode, const char* message) {
    std::cout << "[-] Discord Disconnected! Code: " << errcode << " - " << message << std::endl;
}

void handleDiscordError(int errcode, const char* message) {
    std::cout << "[!] Discord Error! Code: " << errcode << " - " << message << std::endl;
}

// Hàm kích hoạt khi có người bấm THAM GIA
void handleDiscordJoin(const char* secret) {
    int randomIndex = rand() % msgList.size();
    RandomMessage chosen = msgList[randomIndex];

    std::cout << "\n[+] CO NGUOI BAM JOIN! Dang chuyen tiep tin nhan cho Bot..." << std::endl;

    // Ghi tin nhắn bốc được vào file message.txt
    std::ofstream outFile("message.txt");
    if (outFile.is_open()) {
        outFile << chosen.text << " " << chosen.emoji;
        outFile.close();
        std::cout << "[>] Da tao file message.txt thanh cong!" << std::endl;
    } else {
        std::cout << "[X] Loi: Khong the tao file ghi tin nhan!" << std::endl;
    }
}

int main() {
    srand(time(nullptr));

    DiscordEventHandlers handlers;
    memset(&handlers, 0, sizeof(handlers));
    handlers.ready = handleDiscordReady;
    handlers.disconnected = handleDiscordDisconnected;
    handlers.errored = handleDiscordError;
    handlers.joinGame = handleDiscordJoin; // Gán sự kiện
    
    Discord_Initialize(APPLICATION_ID, &handlers, 1, nullptr);
    std::cout << "[*] Connecting to Discord Client... (Bot Bridge Mode Enabled)" << std::endl;
    
    while (true) {
        UpdatePresence();
        Discord_RunCallbacks();
        Sleep(15000); 
    }
    
    Discord_Shutdown();
    return 0;
}
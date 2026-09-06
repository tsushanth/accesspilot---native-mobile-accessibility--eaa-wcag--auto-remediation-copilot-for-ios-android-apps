import SwiftUI

struct ProfileView: View {
    var body: some View {
        VStack {
            Image(systemName: "person.crop.circle")
                .resizable()
                .frame(width: 30, height: 30)

            Button(action: {
                print("Edit profile tapped")
            }) {
                Text("Edit")
            }
        }
    }
}
